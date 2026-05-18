"""Async-transport coverage. Mirrors the sync paths in test_http.py."""

from __future__ import annotations

import httpx
import pytest
import respx

from voicetel import (
    ApiError,
    AsyncClient,
    Client,
    RateLimitError,
)
from voicetel._http import AsyncTransport

BASE = "https://api.voicetel.test"


def make_async(**kw) -> AsyncTransport:
    kw.setdefault("api_key", "k" * 32)
    kw.setdefault("base_url", BASE)
    kw.setdefault("max_retries", 0)
    return AsyncTransport(**kw)


@pytest.mark.asyncio
@respx.mock(base_url=BASE)
async def test_async_retry_on_429(respx_mock: respx.Router) -> None:
    route = respx_mock.get("/v2.2/account").mock(
        side_effect=[
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"status": "success", "data": None}),
        ]
    )
    t = make_async(max_retries=1)
    body = await t.request("GET", "/v2.2/account")
    assert body == {"status": "success", "data": None}
    assert route.call_count == 2
    await t.aclose()


@pytest.mark.asyncio
@respx.mock(base_url=BASE)
async def test_async_retry_exhausted_raises(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(
        return_value=httpx.Response(429, headers={"Retry-After": "0"})
    )
    t = make_async(max_retries=1)
    with pytest.raises(RateLimitError):
        await t.request("GET", "/v2.2/account")
    await t.aclose()


@pytest.mark.asyncio
@respx.mock(base_url=BASE)
async def test_async_transport_error_retries_then_raises(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(side_effect=httpx.ConnectError("boom"))
    t = make_async(max_retries=1)
    with pytest.raises(ApiError) as exc:
        await t.request("GET", "/v2.2/account")
    assert exc.value.status_code == 0
    await t.aclose()


@pytest.mark.asyncio
@respx.mock(base_url=BASE)
async def test_async_transport_error_then_success(respx_mock: respx.Router) -> None:
    respx_mock.get("/v2.2/account").mock(
        side_effect=[
            httpx.ConnectError("boom"),
            httpx.Response(200, json={"status": "success", "data": {}}),
        ]
    )
    t = make_async(max_retries=1)
    body = await t.request("GET", "/v2.2/account")
    assert body == {"status": "success", "data": {}}
    await t.aclose()


@pytest.mark.asyncio
async def test_async_request_without_key_raises() -> None:
    t = AsyncTransport(api_key=None, base_url=BASE, max_retries=0)
    from voicetel import ConfigurationError

    with pytest.raises(ConfigurationError):
        await t.request("GET", "/v2.2/account")
    await t.aclose()


@pytest.mark.asyncio
async def test_async_context_manager() -> None:
    async with AsyncTransport(api_key="k", base_url=BASE, max_retries=0) as t:
        assert t.api_key == "k"


@pytest.mark.asyncio
async def test_async_set_bearer_updates() -> None:
    t = make_async()
    t.set_bearer("new")
    assert t.api_key == "new"
    await t.aclose()


@pytest.mark.asyncio
async def test_async_does_not_close_external_client() -> None:
    http = httpx.AsyncClient(base_url=BASE)
    t = AsyncTransport(api_key="x", base_url=BASE, http_client=http, max_retries=0)
    await t.aclose()
    assert http.is_closed is False
    await http.aclose()


@pytest.mark.asyncio
async def test_async_base_url_trailing_slash_stripped() -> None:
    t = AsyncTransport(api_key="x", base_url=f"{BASE}/", max_retries=0)
    assert t.base_url == BASE
    await t.aclose()


def test_sync_client_base_url_property() -> None:
    with Client(api_key="x", base_url=BASE, max_retries=0) as c:
        assert c.base_url == BASE


@pytest.mark.asyncio
async def test_async_client_base_url_property() -> None:
    async with AsyncClient(api_key="x", base_url=BASE, max_retries=0) as c:
        assert c.base_url == BASE
