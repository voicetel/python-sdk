from __future__ import annotations

from typing import Any

from ..models import E911AddressRequest, E911CreateRequest, E911ProvisionByIdRequest
from ._base import AsyncResource, Resource, unwrap


class E911Resource(Resource):
    """e911 records and address validation."""

    def list(self) -> Any:
        """GET /v2.2/e911 — list e911 records on the account."""
        return unwrap(self._t.request("GET", "/v2.2/e911"))

    def create(self, body: E911CreateRequest) -> Any:
        """POST /v2.2/e911 — validate and provision in one call."""
        return unwrap(self._t.request("POST", "/v2.2/e911", json=body.to_payload()))

    def validate(self, body: E911AddressRequest) -> Any:
        """POST /v2.2/e911/validations — validate an address, returning an addressId."""
        return unwrap(self._t.request("POST", "/v2.2/e911/validations", json=body.to_payload()))

    def get(self, dn: str) -> Any:
        """GET /v2.2/e911/{dn} — e911 record for ``dn``."""
        return unwrap(self._t.request("GET", f"/v2.2/e911/{dn}"))

    def provision(self, dn: str, body: E911ProvisionByIdRequest) -> Any:
        """PUT /v2.2/e911/{dn} — provision ``dn`` with a previously-validated addressId."""
        return unwrap(self._t.request("PUT", f"/v2.2/e911/{dn}", json=body.to_payload()))

    def remove(self, dn: str) -> Any:
        """DELETE /v2.2/e911/{dn} — remove an e911 record."""
        return unwrap(self._t.request("DELETE", f"/v2.2/e911/{dn}"))


class E911AsyncResource(AsyncResource):
    async def list(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/e911"))

    async def create(self, body: E911CreateRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/e911", json=body.to_payload()))

    async def validate(self, body: E911AddressRequest) -> Any:
        return unwrap(
            await self._t.request("POST", "/v2.2/e911/validations", json=body.to_payload())
        )

    async def get(self, dn: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/e911/{dn}"))

    async def provision(self, dn: str, body: E911ProvisionByIdRequest) -> Any:
        return unwrap(
            await self._t.request("PUT", f"/v2.2/e911/{dn}", json=body.to_payload())
        )

    async def remove(self, dn: str) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/e911/{dn}"))
