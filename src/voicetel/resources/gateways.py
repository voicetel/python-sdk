from __future__ import annotations

from ..models import (
    GatewayAddRequest,
    GatewayEntry,
    GatewayNumbersData,
    GatewaysListData,
    GatewayUpdateRequest,
)
from ._base import AsyncResource, Resource, unwrap


class GatewaysResource(Resource):
    """Outbound termination gateways."""

    def list(self) -> GatewaysListData:
        return GatewaysListData.model_validate(unwrap(self._t.request("GET", "/v2.2/gateways")))

    def add(self, body: GatewayAddRequest) -> GatewayEntry:
        return GatewayEntry.model_validate(
            unwrap(self._t.request("POST", "/v2.2/gateways", json=body.to_payload()))
        )

    def get(self, gateway_id: int) -> GatewayEntry:
        return GatewayEntry.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/gateways/{gateway_id}"))
        )

    def update(self, gateway_id: int, body: GatewayUpdateRequest) -> GatewayEntry:
        return GatewayEntry.model_validate(
            unwrap(
                self._t.request("PUT", f"/v2.2/gateways/{gateway_id}", json=body.to_payload())
            )
        )

    def remove(self, gateway_id: int) -> None:
        """DELETE /v2.2/gateways/{id} — returns 204 No Content."""
        self._t.request("DELETE", f"/v2.2/gateways/{gateway_id}")

    def numbers(self, gateway_id: int) -> GatewayNumbersData:
        return GatewayNumbersData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/gateways/{gateway_id}/numbers"))
        )


class GatewaysAsyncResource(AsyncResource):
    async def list(self) -> GatewaysListData:
        return GatewaysListData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/gateways"))
        )

    async def add(self, body: GatewayAddRequest) -> GatewayEntry:
        return GatewayEntry.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/gateways", json=body.to_payload()))
        )

    async def get(self, gateway_id: int) -> GatewayEntry:
        return GatewayEntry.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/gateways/{gateway_id}"))
        )

    async def update(self, gateway_id: int, body: GatewayUpdateRequest) -> GatewayEntry:
        return GatewayEntry.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/gateways/{gateway_id}", json=body.to_payload()
                )
            )
        )

    async def remove(self, gateway_id: int) -> None:
        await self._t.request("DELETE", f"/v2.2/gateways/{gateway_id}")

    async def numbers(self, gateway_id: int) -> GatewayNumbersData:
        return GatewayNumbersData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/gateways/{gateway_id}/numbers"))
        )
