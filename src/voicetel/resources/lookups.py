from __future__ import annotations

from ..models import CarrierData, CnamData, LrnLookupData
from ._base import AsyncResource, Resource, quote_path, unwrap


class LookupsResource(Resource):
    """CNAM, carrier/line-type and LRN dips."""

    def cnam(self, number: str) -> CnamData:
        return CnamData.model_validate(unwrap(self._t.request("GET", f"/v2.2/cnam/{quote_path(number)}")))

    def carrier(self, number: str) -> CarrierData:
        """GET /v2.2/carrier/{number} — carrier and line type, billed as a CNAM query
        only when a result comes back."""
        return CarrierData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/carrier/{quote_path(number)}"))
        )

    def lrn(self, number: str, ani: str) -> LrnLookupData:
        """``ani`` is the presented caller ANI (10 digits); used only for billing/auth."""
        return LrnLookupData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/lrn/{quote_path(number)}/{quote_path(ani)}"))
        )


class LookupsAsyncResource(AsyncResource):
    async def cnam(self, number: str) -> CnamData:
        return CnamData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/cnam/{quote_path(number)}"))
        )

    async def carrier(self, number: str) -> CarrierData:
        return CarrierData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/carrier/{quote_path(number)}"))
        )

    async def lrn(self, number: str, ani: str) -> LrnLookupData:
        return LrnLookupData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/lrn/{quote_path(number)}/{quote_path(ani)}"))
        )
