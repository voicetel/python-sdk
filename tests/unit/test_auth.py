from __future__ import annotations

import httpx
import pytest
import respx

from voicetel import AsyncClient, AuthenticationError, Client
from voicetel._http import AsyncTransport, Transport
from voicetel.auth import aexchange_api_key, exchange_api_key

BASE = "https://api.voicetel.test"


@respx.mock(base_url=BASE)
def test_exchange_api_key_sets_bearer(respx_mock: respx.Router) -> None:
    route = respx_mock.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(
            200, json={"status": "success", "data": {"apikey": "32hex"}}
        )
    )
    t = Transport(api_key=None, base_url=BASE, max_retries=0)
    key = exchange_api_key(t, 1234567890, "secret")
    assert key == "32hex"
    assert t.api_key == "32hex"
    sent = route.calls.last.request
    import json

    assert json.loads(sent.content) == {"username": 1234567890, "password": "secret"}


@respx.mock(base_url=BASE)
def test_exchange_missing_apikey_raises(respx_mock: respx.Router) -> None:
    respx_mock.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": {"wrong": 1}})
    )
    t = Transport(api_key=None, base_url=BASE, max_retries=0)
    with pytest.raises(AuthenticationError):
        exchange_api_key(t, 1, "p")


@respx.mock(base_url=BASE)
def test_exchange_non_dict_response_raises(respx_mock: respx.Router) -> None:
    respx_mock.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(200, json=["unexpected"])
    )
    t = Transport(api_key=None, base_url=BASE, max_retries=0)
    with pytest.raises(AuthenticationError):
        exchange_api_key(t, 1, "p")


@respx.mock(base_url=BASE)
def test_exchange_data_not_dict_raises(respx_mock: respx.Router) -> None:
    respx_mock.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(200, json={"status": "success", "data": "not a dict"})
    )
    t = Transport(api_key=None, base_url=BASE, max_retries=0)
    with pytest.raises(AuthenticationError):
        exchange_api_key(t, 1, "p")


@pytest.mark.asyncio
@respx.mock(base_url=BASE)
async def test_async_exchange_api_key(respx_mock: respx.Router) -> None:
    respx_mock.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(
            200, json={"status": "success", "data": {"apikey": "abc"}}
        )
    )
    t = AsyncTransport(api_key=None, base_url=BASE, max_retries=0)
    key = await aexchange_api_key(t, "1", "p")
    assert key == "abc"
    assert t.api_key == "abc"
    await t.aclose()


@pytest.mark.asyncio
async def test_async_client_login_uses_aexchange(mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(
            200, json={"status": "success", "data": {"apikey": "zz"}}
        )
    )
    async with AsyncClient(api_key=None, base_url=BASE, max_retries=0) as c:
        assert await c.login(1, "p") == "zz"
        assert c.api_key == "zz"


def test_sync_client_login(mock_router: respx.Router) -> None:
    mock_router.post("/v2.2/account/api-key").mock(
        return_value=httpx.Response(
            200, json={"status": "success", "data": {"apikey": "kk"}}
        )
    )
    with Client(api_key=None, base_url=BASE, max_retries=0) as c:
        assert c.login(1, "p") == "kk"
