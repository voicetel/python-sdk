from __future__ import annotations

from typing import Any

from ._http import AsyncTransport, Transport
from .exceptions import ApiError, AuthenticationError

API_KEY_PATH = "/v2.2/account/api-key"


def exchange_api_key(transport: Transport, username: int | str, password: str) -> str:
    """Exchange username/password for a 32-hex API key and install it on ``transport``.

    This is the only endpoint that does not require an Authorization header. Subject to the
    6 req/hour/IP rate limit shared by all ``account/*`` endpoints.
    """
    body = transport.request(
        "POST",
        API_KEY_PATH,
        json={"username": username, "password": password},
        require_auth=False,
    )
    key = _extract_key(body)
    transport.set_bearer(key)
    return key


async def aexchange_api_key(
    transport: AsyncTransport, username: int | str, password: str
) -> str:
    """Async counterpart to :func:`exchange_api_key`."""
    body = await transport.request(
        "POST",
        API_KEY_PATH,
        json={"username": username, "password": password},
        require_auth=False,
    )
    key = _extract_key(body)
    transport.set_bearer(key)
    return key


def _extract_key(body: Any) -> str:
    if isinstance(body, dict):
        data = body.get("data")
        if isinstance(data, dict):
            key = data.get("apikey")
            if isinstance(key, str) and key:
                return key
    raise AuthenticationError(
        "api-key response did not contain data.apikey",
        status_code=200,
        body=body,
    )


__all__ = ["ApiError", "aexchange_api_key", "exchange_api_key"]
