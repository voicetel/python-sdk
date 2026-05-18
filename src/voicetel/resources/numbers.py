from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..models import (
    NumberAddRequest,
    NumberCampaignAssignRequest,
    NumberCnamRequest,
    NumberFaxRequest,
    NumberForwardRequest,
    NumberLibdRequest,
    NumberMessagingPatchRequest,
    NumberMoveRequest,
    NumberRouteRequest,
    NumberSmsRequest,
    NumberTranslationRequest,
    PortOutPinUpdateRequest,
)
from ._base import AsyncResource, Resource, unwrap


class NumbersResource(Resource):
    """Operations on telephone numbers owned by the account."""

    def list(self) -> Any:
        """GET /v2.2/numbers — list numbers on the account."""
        return unwrap(self._t.request("GET", "/v2.2/numbers"))

    def add(self, body: NumberAddRequest) -> Any:
        """POST /v2.2/numbers — attach a number to the account."""
        return unwrap(self._t.request("POST", "/v2.2/numbers", json=body.to_payload()))

    def get(self, number: str) -> Any:
        """GET /v2.2/numbers/{number}"""
        return unwrap(self._t.request("GET", f"/v2.2/numbers/{number}"))

    def remove(self, number: str) -> Any:
        """DELETE /v2.2/numbers/{number}"""
        return unwrap(self._t.request("DELETE", f"/v2.2/numbers/{number}"))

    def move(self, number: str, body: NumberMoveRequest) -> Any:
        """PATCH /v2.2/numbers/{number} — move to another account."""
        return unwrap(
            self._t.request("PATCH", f"/v2.2/numbers/{number}", json=body.to_payload())
        )

    def release(self, number: str) -> Any:
        """POST /v2.2/numbers/{number}/release — release back to the network."""
        return unwrap(self._t.request("POST", f"/v2.2/numbers/{number}/release"))

    def set_route(self, number: str, body: NumberRouteRequest) -> Any:
        """PUT /v2.2/numbers/{number}/route"""
        return unwrap(
            self._t.request("PUT", f"/v2.2/numbers/{number}/route", json=body.to_payload())
        )

    def set_translation(self, number: str, body: NumberTranslationRequest) -> Any:
        """PUT /v2.2/numbers/{number}/translation"""
        return unwrap(
            self._t.request(
                "PUT", f"/v2.2/numbers/{number}/translation", json=body.to_payload()
            )
        )

    def set_cnam(self, number: str, body: NumberCnamRequest) -> Any:
        """PUT /v2.2/numbers/{number}/cnam — inbound CNAM toggle."""
        return unwrap(
            self._t.request("PUT", f"/v2.2/numbers/{number}/cnam", json=body.to_payload())
        )

    def set_lidb(self, number: str, body: NumberLibdRequest) -> Any:
        """PUT /v2.2/numbers/{number}/lidb — outbound CNAM (caller name)."""
        return unwrap(
            self._t.request("PUT", f"/v2.2/numbers/{number}/lidb", json=body.to_payload())
        )

    def get_fax(self, number: str) -> Any:
        return unwrap(self._t.request("GET", f"/v2.2/numbers/{number}/fax"))

    def set_fax(self, number: str, body: NumberFaxRequest) -> Any:
        return unwrap(
            self._t.request("PUT", f"/v2.2/numbers/{number}/fax", json=body.to_payload())
        )

    def remove_fax(self, number: str) -> Any:
        return unwrap(self._t.request("DELETE", f"/v2.2/numbers/{number}/fax"))

    def set_forward(self, number: str, body: NumberForwardRequest) -> Any:
        return unwrap(
            self._t.request("PUT", f"/v2.2/numbers/{number}/forward", json=body.to_payload())
        )

    def remove_forward(self, number: str) -> Any:
        return unwrap(self._t.request("DELETE", f"/v2.2/numbers/{number}/forward"))

    def get_sms(self, number: str) -> Any:
        return unwrap(self._t.request("GET", f"/v2.2/numbers/{number}/sms"))

    def set_sms(self, number: str, body: NumberSmsRequest) -> Any:
        return unwrap(
            self._t.request("PUT", f"/v2.2/numbers/{number}/sms", json=body.to_payload())
        )

    def remove_sms(self, number: str) -> Any:
        return unwrap(self._t.request("DELETE", f"/v2.2/numbers/{number}/sms"))

    def get_messaging(self, number: str) -> Any:
        return unwrap(self._t.request("GET", f"/v2.2/numbers/{number}/messaging"))

    def patch_messaging(
        self, number: str, body: NumberMessagingPatchRequest
    ) -> Any:
        return unwrap(
            self._t.request(
                "PATCH", f"/v2.2/numbers/{number}/messaging", json=body.to_payload()
            )
        )

    def assign_campaign(
        self, number: str, body: NumberCampaignAssignRequest
    ) -> Any:
        return unwrap(
            self._t.request(
                "PUT", f"/v2.2/numbers/{number}/messaging-campaign", json=body.to_payload()
            )
        )

    def unassign_campaign(self, number: str) -> Any:
        return unwrap(
            self._t.request("DELETE", f"/v2.2/numbers/{number}/messaging-campaign")
        )

    def bulk_unassign_campaign(self, numbers: Sequence[str]) -> Any:
        return unwrap(
            self._t.request(
                "DELETE",
                "/v2.2/numbers/messaging-campaign",
                json={"numbers": numbers},
            )
        )

    def set_port_out_pin(self, number: str, body: PortOutPinUpdateRequest) -> Any:
        return unwrap(
            self._t.request(
                "PATCH", f"/v2.2/numbers/{number}/port-out-pin", json=body.to_payload()
            )
        )


class NumbersAsyncResource(AsyncResource):
    async def list(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/numbers"))

    async def add(self, body: NumberAddRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/numbers", json=body.to_payload()))

    async def get(self, number: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}"))

    async def remove(self, number: str) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/numbers/{number}"))

    async def move(self, number: str, body: NumberMoveRequest) -> Any:
        return unwrap(
            await self._t.request("PATCH", f"/v2.2/numbers/{number}", json=body.to_payload())
        )

    async def release(self, number: str) -> Any:
        return unwrap(await self._t.request("POST", f"/v2.2/numbers/{number}/release"))

    async def set_route(self, number: str, body: NumberRouteRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/route", json=body.to_payload()
            )
        )

    async def set_translation(
        self, number: str, body: NumberTranslationRequest
    ) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/translation", json=body.to_payload()
            )
        )

    async def set_cnam(self, number: str, body: NumberCnamRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/cnam", json=body.to_payload()
            )
        )

    async def set_lidb(self, number: str, body: NumberLibdRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/lidb", json=body.to_payload()
            )
        )

    async def get_fax(self, number: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}/fax"))

    async def set_fax(self, number: str, body: NumberFaxRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/fax", json=body.to_payload()
            )
        )

    async def remove_fax(self, number: str) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/numbers/{number}/fax"))

    async def set_forward(self, number: str, body: NumberForwardRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/forward", json=body.to_payload()
            )
        )

    async def remove_forward(self, number: str) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/numbers/{number}/forward"))

    async def get_sms(self, number: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}/sms"))

    async def set_sms(self, number: str, body: NumberSmsRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/sms", json=body.to_payload()
            )
        )

    async def remove_sms(self, number: str) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/numbers/{number}/sms"))

    async def get_messaging(self, number: str) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}/messaging"))

    async def patch_messaging(
        self, number: str, body: NumberMessagingPatchRequest
    ) -> Any:
        return unwrap(
            await self._t.request(
                "PATCH", f"/v2.2/numbers/{number}/messaging", json=body.to_payload()
            )
        )

    async def assign_campaign(
        self, number: str, body: NumberCampaignAssignRequest
    ) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/numbers/{number}/messaging-campaign", json=body.to_payload()
            )
        )

    async def unassign_campaign(self, number: str) -> Any:
        return unwrap(
            await self._t.request("DELETE", f"/v2.2/numbers/{number}/messaging-campaign")
        )

    async def bulk_unassign_campaign(self, numbers: Sequence[str]) -> Any:
        return unwrap(
            await self._t.request(
                "DELETE",
                "/v2.2/numbers/messaging-campaign",
                json={"numbers": numbers},
            )
        )

    async def set_port_out_pin(
        self, number: str, body: PortOutPinUpdateRequest
    ) -> Any:
        return unwrap(
            await self._t.request(
                "PATCH", f"/v2.2/numbers/{number}/port-out-pin", json=body.to_payload()
            )
        )
