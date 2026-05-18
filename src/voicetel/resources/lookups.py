from __future__ import annotations

from typing import Any

from ._base import AsyncResource, Resource, unwrap


class LookupsResource(Resource):
    """CNAM and LRN dips."""

    def cnam(self, number: str) -> Any:
        """GET /v2.2/cnam/{number} — caller name for the given 10-digit number."""
        return unwrap(self._t.request("GET", f"/v2.2/cnam/{number}"))

    def lrn(self, number: str, ani: str) -> Any:
        """GET /v2.2/lrn/{number}/{ani} — Local Routing Number dip.

        ``ani`` is the 10-digit ANI presented as the caller; it is used only for billing/auth and
        is not echoed in the response.
        """
        return unwrap(self._t.request("GET", f"/v2.2/lrn/{number}/{ani}"))


class LookupsAsyncResource(AsyncResource):
    async def cnam(self, number: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/cnam/{number}"))

    async def lrn(self, number: str, ani: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/lrn/{number}/{ani}"))
