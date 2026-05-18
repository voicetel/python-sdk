from __future__ import annotations

from ..models import AuthGetData, AuthPutData, AuthPutRequest
from ._base import AsyncResource, Resource, unwrap


class AuthenticationResource(Resource):
    """SIP/HTTP authentication settings."""

    def get(self) -> AuthGetData:
        return AuthGetData.model_validate(unwrap(self._t.request("GET", "/v2.2/auth")))

    def update(self, body: AuthPutRequest) -> AuthPutData:
        return AuthPutData.model_validate(
            unwrap(self._t.request("PUT", "/v2.2/auth", json=body.to_payload()))
        )


class AuthenticationAsyncResource(AsyncResource):
    async def get(self) -> AuthGetData:
        return AuthGetData.model_validate(unwrap(await self._t.request("GET", "/v2.2/auth")))

    async def update(self, body: AuthPutRequest) -> AuthPutData:
        return AuthPutData.model_validate(
            unwrap(await self._t.request("PUT", "/v2.2/auth", json=body.to_payload()))
        )
