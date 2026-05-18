from __future__ import annotations

from ..models import AclAddData, AclListData, AclModifyRequest, AclRemoveData
from ._base import AsyncResource, Resource, unwrap


class AclResource(Resource):
    """IP-based access control list."""

    def list(self) -> AclListData:
        return AclListData.model_validate(unwrap(self._t.request("GET", "/v2.2/acl")))

    def add(self, body: AclModifyRequest) -> AclAddData:
        return AclAddData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/acl", json=body.to_payload()))
        )

    def remove(self, body: AclModifyRequest) -> AclRemoveData:
        return AclRemoveData.model_validate(
            unwrap(self._t.request("DELETE", "/v2.2/acl", json=body.to_payload()))
        )


class AclAsyncResource(AsyncResource):
    async def list(self) -> AclListData:
        return AclListData.model_validate(unwrap(await self._t.request("GET", "/v2.2/acl")))

    async def add(self, body: AclModifyRequest) -> AclAddData:
        return AclAddData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/acl", json=body.to_payload()))
        )

    async def remove(self, body: AclModifyRequest) -> AclRemoveData:
        return AclRemoveData.model_validate(
            unwrap(await self._t.request("DELETE", "/v2.2/acl", json=body.to_payload()))
        )
