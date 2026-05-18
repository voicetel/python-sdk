from __future__ import annotations

from typing import Any

from ..models import AuthPutRequest
from ._base import AsyncResource, Resource, unwrap


class AuthenticationResource(Resource):
    """SIP/HTTP authentication settings."""

    def get(self) -> Any:
        """GET /v2.2/auth — current auth settings."""
        return unwrap(self._t.request("GET", "/v2.2/auth"))

    def update(self, body: AuthPutRequest) -> Any:
        """PUT /v2.2/auth — update auth type and/or password."""
        return unwrap(self._t.request("PUT", "/v2.2/auth", json=body.to_payload()))


class AuthenticationAsyncResource(AsyncResource):
    async def get(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/auth"))

    async def update(self, body: AuthPutRequest) -> Any:
        return unwrap(await self._t.request("PUT", "/v2.2/auth", json=body.to_payload()))
