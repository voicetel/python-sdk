from __future__ import annotations

from ..models import CnamData, LrnLookupData
from ._base import AsyncResource, Resource, unwrap


class LookupsResource(Resource):
    """CNAM and LRN dips."""

    def cnam(self, number: str) -> CnamData:
        return CnamData.model_validate(unwrap(self._t.request("GET", f"/v2.2/cnam/{number}")))

    def lrn(self, number: str, ani: str) -> LrnLookupData:
        """``ani`` is the presented caller ANI (10 digits); used only for billing/auth."""
        return LrnLookupData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/lrn/{number}/{ani}"))
        )


class LookupsAsyncResource(AsyncResource):
    async def cnam(self, number: str) -> CnamData:
        return CnamData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/cnam/{number}"))
        )

    async def lrn(self, number: str, ani: str) -> LrnLookupData:
        return LrnLookupData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/lrn/{number}/{ani}"))
        )
