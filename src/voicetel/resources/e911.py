from __future__ import annotations

from ..models import (
    E911AddressRequest,
    E911AllData,
    E911CreateRequest,
    E911ProvisionByIdRequest,
    E911RecordData,
    E911ValidateData,
)
from ._base import AsyncResource, Resource, unwrap


class E911Resource(Resource):
    """e911 records and address validation."""

    def list(self) -> E911AllData:
        return E911AllData.model_validate(unwrap(self._t.request("GET", "/v2.2/e911")))

    def create(self, body: E911CreateRequest) -> E911RecordData:
        return E911RecordData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/e911", json=body.to_payload()))
        )

    def validate(self, body: E911AddressRequest) -> E911ValidateData:
        return E911ValidateData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/e911/validations", json=body.to_payload()))
        )

    def get(self, dn: str) -> E911RecordData:
        return E911RecordData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/e911/{dn}"))
        )

    def provision(self, dn: str, body: E911ProvisionByIdRequest) -> E911RecordData:
        return E911RecordData.model_validate(
            unwrap(self._t.request("PUT", f"/v2.2/e911/{dn}", json=body.to_payload()))
        )

    def remove(self, dn: str) -> None:
        """DELETE /v2.2/e911/{dn} — returns 204 No Content."""
        self._t.request("DELETE", f"/v2.2/e911/{dn}")


class E911AsyncResource(AsyncResource):
    async def list(self) -> E911AllData:
        return E911AllData.model_validate(unwrap(await self._t.request("GET", "/v2.2/e911")))

    async def create(self, body: E911CreateRequest) -> E911RecordData:
        return E911RecordData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/e911", json=body.to_payload()))
        )

    async def validate(self, body: E911AddressRequest) -> E911ValidateData:
        return E911ValidateData.model_validate(
            unwrap(
                await self._t.request("POST", "/v2.2/e911/validations", json=body.to_payload())
            )
        )

    async def get(self, dn: str) -> E911RecordData:
        return E911RecordData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/e911/{dn}"))
        )

    async def provision(self, dn: str, body: E911ProvisionByIdRequest) -> E911RecordData:
        return E911RecordData.model_validate(
            unwrap(await self._t.request("PUT", f"/v2.2/e911/{dn}", json=body.to_payload()))
        )

    async def remove(self, dn: str) -> None:
        await self._t.request("DELETE", f"/v2.2/e911/{dn}")
