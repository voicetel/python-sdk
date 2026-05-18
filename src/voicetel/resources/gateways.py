from __future__ import annotations

from typing import Any

from ..models import GatewayAddRequest, GatewayUpdateRequest
from ._base import AsyncResource, Resource, unwrap


class GatewaysResource(Resource):
    """Outbound termination gateways."""

    def list(self) -> Any:
        """GET /v2.2/gateways — list gateways."""
        return unwrap(self._t.request("GET", "/v2.2/gateways"))

    def add(self, body: GatewayAddRequest) -> Any:
        """POST /v2.2/gateways — create a gateway."""
        return unwrap(self._t.request("POST", "/v2.2/gateways", json=body.to_payload()))

    def get(self, gateway_id: int) -> Any:
        """GET /v2.2/gateways/{id} — fetch a single gateway."""
        return unwrap(self._t.request("GET", f"/v2.2/gateways/{gateway_id}"))

    def update(self, gateway_id: int, body: GatewayUpdateRequest) -> Any:
        """PUT /v2.2/gateways/{id} — update a gateway."""
        return unwrap(
            self._t.request("PUT", f"/v2.2/gateways/{gateway_id}", json=body.to_payload())
        )

    def remove(self, gateway_id: int) -> Any:
        """DELETE /v2.2/gateways/{id} — delete a gateway."""
        return unwrap(self._t.request("DELETE", f"/v2.2/gateways/{gateway_id}"))

    def numbers(self, gateway_id: int) -> Any:
        """GET /v2.2/gateways/{id}/numbers — numbers routed via this gateway."""
        return unwrap(self._t.request("GET", f"/v2.2/gateways/{gateway_id}/numbers"))


class GatewaysAsyncResource(AsyncResource):
    async def list(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/gateways"))

    async def add(self, body: GatewayAddRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/gateways", json=body.to_payload()))

    async def get(self, gateway_id: int) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/gateways/{gateway_id}"))

    async def update(self, gateway_id: int, body: GatewayUpdateRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/gateways/{gateway_id}", json=body.to_payload()
            )
        )

    async def remove(self, gateway_id: int) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/gateways/{gateway_id}"))

    async def numbers(self, gateway_id: int) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/gateways/{gateway_id}/numbers"))
