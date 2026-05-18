from __future__ import annotations

from typing import Any

from ..models import AclModifyRequest
from ._base import AsyncResource, Resource, unwrap


class AclResource(Resource):
    """IP-based access control list."""

    def list(self) -> Any:
        """GET /v2.2/acl — list current CIDR entries."""
        return unwrap(self._t.request("GET", "/v2.2/acl"))

    def add(self, body: AclModifyRequest) -> Any:
        """POST /v2.2/acl — add CIDR entries."""
        return unwrap(self._t.request("POST", "/v2.2/acl", json=body.to_payload()))

    def remove(self, body: AclModifyRequest) -> Any:
        """DELETE /v2.2/acl — remove CIDR entries."""
        return unwrap(self._t.request("DELETE", "/v2.2/acl", json=body.to_payload()))


class AclAsyncResource(AsyncResource):
    async def list(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/acl"))

    async def add(self, body: AclModifyRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/acl", json=body.to_payload()))

    async def remove(self, body: AclModifyRequest) -> Any:
        return unwrap(await self._t.request("DELETE", "/v2.2/acl", json=body.to_payload()))
