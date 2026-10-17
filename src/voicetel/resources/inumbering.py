from __future__ import annotations

from typing import Literal

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
from ._base import AsyncResource, Resource, quote_path, unwrap

InventoryCountBy = Literal["state", "city", "rateCenter", "npanxx", "block"]


class INumberingResource(Resource):
    """Number inventory, ordering, and porting."""

    def search_inventory(
        self,
        *,
        tn_mask: str,
        quantity: int | None = None,
        province: str | None = None,
        rate_center: str | None = None,
        lata: str | None = None,
    ) -> InventorySearchData:
        """GET /v2.2/inventory — search assignable TNs.

        ``tn_mask`` (required) is a prefix or wildcard pattern (``201``, ``201555``,
        ``201555*``). ``quantity`` is 1-1000 (server default 10).
        """
        return InventorySearchData.model_validate(
            unwrap(
                self._t.request(
                    "GET",
                    "/v2.2/inventory",
                    params={
                        "tnMask": tn_mask,
                        "quantity": quantity,
                        "province": province,
                        "rateCenter": rate_center,
                        "lata": lata,
                    },
                )
            )
        )

    def coverage(
        self,
        *,
        count_by: InventoryCountBy,
        loc_state: str | None = None,
        city: str | None = None,
        rc_abbre: str | None = None,
        npa: str | None = None,
        lata: str | None = None,
    ) -> InventoryCoverageData:
        """GET /v2.2/inventory/coverage — aggregated availability buckets.

        ``count_by`` (required) selects the grouping: ``state``, ``city``,
        ``rateCenter``, ``npanxx`` or ``block``.
        """
        return InventoryCoverageData.model_validate(
            unwrap(
                self._t.request(
                    "GET",
                    "/v2.2/inventory/coverage",
                    params={
                        "countBy": count_by,
                        "locState": loc_state,
                        "city": city,
                        "rcAbbre": rc_abbre,
                        "npa": npa,
                        "lata": lata,
                    },
                )
            )
        )

    def order(self, body: OrderCreateRequest) -> OrderCreateData:
        return OrderCreateData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/orders", json=body.to_payload()))
        )

    def ports(self) -> PortListData:
        return PortListData.model_validate(unwrap(self._t.request("GET", "/v2.2/ports")))

    def port(self, port_id: str) -> PortDetailData:
        """GET /v2.2/ports/{id} — ``port_id`` is the 5-character alphanumeric pid."""
        return PortDetailData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/ports/{quote_path(port_id)}"))
        )

    def submit_port(self, body: PortSubmitRequest) -> PortSubmitData:
        return PortSubmitData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/ports", json=body.to_payload()))
        )

    def port_availability(self, number: str) -> PortAvailabilityData:
        return PortAvailabilityData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/ports/availability/{quote_path(number)}"))
        )


class INumberingAsyncResource(AsyncResource):
    async def search_inventory(
        self,
        *,
        tn_mask: str,
        quantity: int | None = None,
        province: str | None = None,
        rate_center: str | None = None,
        lata: str | None = None,
    ) -> InventorySearchData:
        """GET /v2.2/inventory — search assignable TNs.

        ``tn_mask`` (required) is a prefix or wildcard pattern (``201``, ``201555``,
        ``201555*``). ``quantity`` is 1-1000 (server default 10).
        """
        return InventorySearchData.model_validate(
            unwrap(
                await self._t.request(
                    "GET",
                    "/v2.2/inventory",
                    params={
                        "tnMask": tn_mask,
                        "quantity": quantity,
                        "province": province,
                        "rateCenter": rate_center,
                        "lata": lata,
                    },
                )
            )
        )

    async def coverage(
        self,
        *,
        count_by: InventoryCountBy,
        loc_state: str | None = None,
        city: str | None = None,
        rc_abbre: str | None = None,
        npa: str | None = None,
        lata: str | None = None,
    ) -> InventoryCoverageData:
        """GET /v2.2/inventory/coverage — aggregated availability buckets.

        ``count_by`` (required) selects the grouping: ``state``, ``city``,
        ``rateCenter``, ``npanxx`` or ``block``.
        """
        return InventoryCoverageData.model_validate(
            unwrap(
                await self._t.request(
                    "GET",
                    "/v2.2/inventory/coverage",
                    params={
                        "countBy": count_by,
                        "locState": loc_state,
                        "city": city,
                        "rcAbbre": rc_abbre,
                        "npa": npa,
                        "lata": lata,
                    },
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

    async def port(self, port_id: str) -> PortDetailData:
        """GET /v2.2/ports/{id} — ``port_id`` is the 5-character alphanumeric pid."""
        return PortDetailData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/ports/{quote_path(port_id)}"))
        )

    async def submit_port(self, body: PortSubmitRequest) -> PortSubmitData:
        return PortSubmitData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/ports", json=body.to_payload()))
        )

    async def port_availability(self, number: str) -> PortAvailabilityData:
        return PortAvailabilityData.model_validate(
            unwrap(
                await self._t.request(
                    "GET", f"/v2.2/ports/availability/{quote_path(number)}"
                )
            )
        )
