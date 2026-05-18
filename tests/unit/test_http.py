from __future__ import annotations

import httpx
import pytest
import respx

from voicetel import (
    ApiError,
    AuthenticationError,
    BadRequestError,
    Client,
    ConfigurationError,
    NotFoundError,
    RateLimitError,
)
from voicetel._http import (
    DEFAULT_BASE_URL,
    DEFAULT_USER_AGENT,
    AsyncTransport,
    Transport,
    _backoff_delay,
    _clean_params,
)

BASE = "https://api.voicetel.test"


def make_transport(**kw) -> Transport:
    kw.setdefault("api_key", "k" * 32)
    kw.setdefault("base_url", BASE)
    kw.setdefault("max_retries", 0)
    return Transport(**kw)


@respx.mock(base_url=BASE)
def test_request_attaches_bearer_and_user_agent(respx_mock: respx.Router) -> None:
    route = respx_mock.get("/v2.2/account").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": {}})
    )
    t = make_transport()
    assert t.request("GET", "/v2.2/account") == {"status": "success", "data": {}}
    sent = route.calls.last.request
    assert sent.headers["Authorization"] == f"Bearer {'k' * 32}"
    assert sent.headers["User-Agent"] == DEFAULT_USER_AGENT
    assert sent.headers["Accept"] == "application/json"


@respx.mock(base_url=BASE)
def test_request_omits_auth_when_not_required(respx_mock: respx.Router) -> None:
    route = respx_mock.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": {"apikey": "x"}})
    )
    t = Transport(api_key=None, base_url=BASE, max_retries=0)
    t.request("POST", "/v2.2/account/api-key", json={"u": 1, "p": "p"}, require_auth=False)
    assert "Authorization" not in route.calls.last.request.headers


def test_request_without_key_raises_when_auth_required() -> None:
    t = Transport(api_key=None, base_url=BASE, max_retries=0)
    with pytest.raises(ConfigurationError):
        t.request("GET", "/v2.2/account")


def test_negative_max_retries_rejected() -> None:
    with pytest.raises(ConfigurationError):
        Transport(api_key="x", max_retries=-1)


def test_negative_max_retries_rejected_async() -> None:
    with pytest.raises(ConfigurationError):
        AsyncTransport(api_key="x", max_retries=-1)


@respx.mock(base_url=BASE)
def test_status_400_raises_bad_request(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(
        return_value=httpx.Response(
            400, json={"status": "error", "code": "BAD", "message": "no good"}
        )
    )
    with pytest.raises(BadRequestError) as exc:
        make_transport().request("GET", "/v2.2/account")
    assert exc.value.code == "BAD"
    assert "no good" in str(exc.value)


@respx.mock(base_url=BASE)
def test_status_401_raises_authentication_error(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(return_value=httpx.Response(401, json={"error": "nope"}))
    with pytest.raises(AuthenticationError):
        make_transport().request("GET", "/v2.2/account")


@respx.mock(base_url=BASE)
def test_status_404_raises_not_found(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/numbers/x").mock(return_value=httpx.Response(404, text="plain text"))
    with pytest.raises(NotFoundError) as exc:
        make_transport().request("GET", "/v2.2/numbers/x")
    assert exc.value.body == "plain text"


@respx.mock(base_url=BASE)
def test_retry_on_429_then_success(respx_mock: respx.Router) -> None:
    route = respx_mock.get("/v2.2/account").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"status": "success", "data": {"ok": True}}),
        ]
    )
    t = make_transport(max_retries=2)
    body = t.request("GET", "/v2.2/account")
    assert body["data"] == {"ok": True}
    assert route.call_count == 2


@respx.mock(base_url=BASE)
def test_retry_exhausted_raises_rate_limit(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "0"})
    )
    with pytest.raises(RateLimitError):
        make_transport(max_retries=1).request("GET", "/v2.2/account")


@respx.mock(base_url=BASE)
def test_retry_on_503(respx_mock: respx.Router) -> None:
    route = respx_mock.get("/v2.2/account").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json={"status": "success", "data": None}),
        ]
    )
    body = make_transport(max_retries=1).request("GET", "/v2.2/account")
    assert body == {"status": "success", "data": None}
    assert route.call_count == 2


@respx.mock(base_url=BASE)
def test_transport_error_retries_then_raises_api_error(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(side_effect=httpx.ConnectError("boom"))
    with pytest.raises(ApiError) as exc:
        make_transport(max_retries=1).request("GET", "/v2.2/account")
    assert exc.value.status_code == 0
    assert "transport error" in str(exc.value)


@respx.mock(base_url=BASE)
def test_transport_error_then_success(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(
        side_effect=[
            httpx.ConnectError("boom"),
            httpx.Response(200, json={"status": "success", "data": {}}),
        ]
    )
    body = make_transport(max_retries=1).request("GET", "/v2.2/account")
    assert body == {"status": "success", "data": {}}


@respx.mock(base_url=BASE)
def test_empty_204_returns_none(respx_mock: respx.Router) -> None:
    respx_mock.delete("/v2.2/acl").mock(return_value=httpx.Response(204))
    assert make_transport().request("DELETE", "/v2.2/acl") is None


@respx.mock(base_url=BASE)
def test_non_json_success_raises_api_error(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(return_value=httpx.Response(200, text="hi"))
    with pytest.raises(ApiError) as exc:
        make_transport().request("GET", "/v2.2/account")
    assert exc.value.status_code == 200


@respx.mock(base_url=BASE)
def test_query_params_drop_none_values(respx_mock: respx.Router) -> None:
    route = respx_mock.get("/v2.2/inventory").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": []})
    )
    make_transport().request(
        "GET", "/v2.2/inventory", params={"state": "NJ", "limit": None}
    )
    url = route.calls.last.request.url
    assert "state=NJ" in str(url) and "limit" not in str(url)


def test_set_bearer_updates_token() -> None:
    t = make_transport()
    t.set_bearer("new")
    assert t.api_key == "new"


def test_base_url_trailing_slash_stripped() -> None:
    t = Transport(api_key="x", base_url=f"{BASE}/", max_retries=0)
    assert t.base_url == BASE


def test_default_base_url_is_production() -> None:
    t = Transport(api_key="x")
    assert t.base_url == DEFAULT_BASE_URL
    t.close()


def test_clean_params_passthroughs_none() -> None:
    assert _clean_params(None) is None
    assert _clean_params({"a": 1, "b": None}) == {"a": 1}


def test_backoff_caps_at_8s() -> None:
    assert _backoff_delay(0) == 0.5
    assert _backoff_delay(1) == 1.0
    assert _backoff_delay(20) == 8.0


def test_backoff_uses_retry_after_when_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    r = httpx.Response(429, headers={"Retry-After": "0"})
    assert _backoff_delay(0, r) == 0.0


def test_backoff_falls_back_when_retry_after_unparseable() -> None:
    r = httpx.Response(429, headers={"Retry-After": "not-a-number"})
    # Falls through to exponential
    assert _backoff_delay(0, r) == 0.5


def test_transport_close_idempotent_when_owns_client() -> None:
    t = make_transport()
    t.close()
    # Closing again should not error
    t.close()


def test_transport_does_not_close_externally_provided_client() -> None:
    http = httpx.Client(base_url=BASE)
    t = Transport(api_key="x", base_url=BASE, http_client=http, max_retries=0)
    t.close()
    # External client is still open
    assert http.is_closed is False
    http.close()


def test_context_manager_closes() -> None:
    with make_transport() as t:
        assert t.api_key == "k" * 32


def test_client_login_then_request(mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": {"apikey": "abcd"}})
    )
    mock_router.get("/v2.2/account").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": {"me": 1}})
    )
    with Client(api_key=None, base_url=BASE, max_retries=0) as c:
        key = c.login(1234567890, "pw")
        assert key == "abcd"
        assert c.api_key == "abcd"
        assert c.account.get() == {"me": 1}


def test_client_login_with_bad_response_raises(mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": {}})
    )
    with pytest.raises(AuthenticationError):
        Client(api_key=None, base_url=BASE, max_retries=0).login(1, "p")
