from __future__ import annotations

from collections.abc import Sequence

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

    def remove(self, *, cidrs: Sequence[str]) -> AclRemoveData:
        """DELETE /v2.2/acl — remove CIDR entries via the required ``cidrs`` query param."""
        return AclRemoveData.model_validate(
            unwrap(
                self._t.request("DELETE", "/v2.2/acl", params={"cidrs": ",".join(cidrs)})
            )
        )


class AclAsyncResource(AsyncResource):
    async def list(self) -> AclListData:
        return AclListData.model_validate(unwrap(await self._t.request("GET", "/v2.2/acl")))

    async def add(self, body: AclModifyRequest) -> AclAddData:
        return AclAddData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/acl", json=body.to_payload()))
        )

    async def remove(self, *, cidrs: Sequence[str]) -> AclRemoveData:
        """DELETE /v2.2/acl — remove CIDR entries via the required ``cidrs`` query param."""
        return AclRemoveData.model_validate(
            unwrap(
                await self._t.request(
                    "DELETE", "/v2.2/acl", params={"cidrs": ",".join(cidrs)}
                )
            )
        )
