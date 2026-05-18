from __future__ import annotations

from ..models import (
    InventoryCoverageData,
    InventorySearchData,
    OrderCreateData,
    OrderCreateRequest,
    PortAvailabilityData,
    PortDetailData,
    PortListData,
    PortSubmitData,
    PortSubmitRequest,
)
from ._base import AsyncResource, Resource, unwrap


class INumberingResource(Resource):
    """Number inventory, ordering, and porting."""

    def search_inventory(
        self,
        *,
        npa: int | None = None,
        nxx: int | None = None,
        state: str | None = None,
        ratecenter: str | None = None,
        contains: str | None = None,
        endswith: str | None = None,
        limit: int | None = None,
    ) -> InventorySearchData:
        return InventorySearchData.model_validate(
            unwrap(
                self._t.request(
                    "GET",
                    "/v2.2/inventory",
                    params={
                        "npa": npa,
                        "nxx": nxx,
                        "state": state,
                        "ratecenter": ratecenter,
                        "contains": contains,
                        "endswith": endswith,
                        "limit": limit,
                    },
                )
            )
        )

    def coverage(
        self, *, state: str | None = None, ratecenter: str | None = None
    ) -> InventoryCoverageData:
        return InventoryCoverageData.model_validate(
            unwrap(
                self._t.request(
                    "GET",
                    "/v2.2/inventory/coverage",
                    params={"state": state, "ratecenter": ratecenter},
                )
            )
        )

    def order(self, body: OrderCreateRequest) -> OrderCreateData:
        return OrderCreateData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/orders", json=body.to_payload()))
        )

    def ports(self) -> PortListData:
        return PortListData.model_validate(unwrap(self._t.request("GET", "/v2.2/ports")))

    def port(self, port_id: int) -> PortDetailData:
        return PortDetailData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/ports/{port_id}"))
        )

    def submit_port(self, body: PortSubmitRequest) -> PortSubmitData:
        return PortSubmitData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/ports", json=body.to_payload()))
        )

    def port_availability(self, number: str) -> PortAvailabilityData:
        return PortAvailabilityData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/ports/availability/{number}"))
        )


class INumberingAsyncResource(AsyncResource):
    async def search_inventory(
        self,
        *,
        npa: int | None = None,
        nxx: int | None = None,
        state: str | None = None,
        ratecenter: str | None = None,
        contains: str | None = None,
        endswith: str | None = None,
        limit: int | None = None,
    ) -> InventorySearchData:
        return InventorySearchData.model_validate(
            unwrap(
                await self._t.request(
                    "GET",
                    "/v2.2/inventory",
                    params={
                        "npa": npa,
                        "nxx": nxx,
                        "state": state,
                        "ratecenter": ratecenter,
                        "contains": contains,
                        "endswith": endswith,
                        "limit": limit,
                    },
                )
            )
        )

    async def coverage(
        self, *, state: str | None = None, ratecenter: str | None = None
    ) -> InventoryCoverageData:
        return InventoryCoverageData.model_validate(
            unwrap(
                await self._t.request(
                    "GET",
                    "/v2.2/inventory/coverage",
                    params={"state": state, "ratecenter": ratecenter},
                )
            )
        )

    async def order(self, body: OrderCreateRequest) -> OrderCreateData:
        return OrderCreateData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/orders", json=body.to_payload()))
        )

    async def ports(self) -> PortListData:
        return PortListData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/ports"))
        )

    async def port(self, port_id: int) -> PortDetailData:
        return PortDetailData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/ports/{port_id}"))
        )

    async def submit_port(self, body: PortSubmitRequest) -> PortSubmitData:
        return PortSubmitData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/ports", json=body.to_payload()))
        )

    async def port_availability(self, number: str) -> PortAvailabilityData:
        return PortAvailabilityData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/ports/availability/{number}"))
        )
