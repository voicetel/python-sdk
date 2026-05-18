from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    NumberAddData,
    NumberAddRequest,
    NumberCampaignAssignRequest,
    NumberCnamData,
    NumberCnamRequest,
    NumberDetail,
    NumberFaxData,
    NumberFaxRequest,
    NumberForwardData,
    NumberForwardRequest,
    NumberLidbData,
    NumberLidbRequest,
    NumberMessagingCampaignAssignData,
    NumberMessagingCampaignUnassignData,
    NumberMessagingPatchData,
    NumberMessagingPatchRequest,
    NumberMessagingState,
    NumberMoveData,
    NumberMoveRequest,
    NumberRouteData,
    NumberRouteRequest,
    NumbersListData,
    NumbersMessagingCampaignUnassignData,
    NumberSmsData,
    NumberSmsRequest,
    NumberTranslationData,
    NumberTranslationRequest,
    PortOutPinUpdateData,
    PortOutPinUpdateRequest,
)
from ._base import AsyncResource, Resource, unwrap


class NumbersResource(Resource):
    """Operations on telephone numbers owned by the account."""

    def list(self) -> NumbersListData:
        return NumbersListData.model_validate(unwrap(self._t.request("GET", "/v2.2/numbers")))

    def add(self, body: NumberAddRequest) -> NumberAddData:
        return NumberAddData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/numbers", json=body.to_payload()))
        )

    def get(self, number: str) -> NumberDetail:
        return NumberDetail.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/numbers/{number}"))
        )

    def remove(self, number: str) -> None:
        """DELETE /v2.2/numbers/{number} — returns 204 No Content."""
        self._t.request("DELETE", f"/v2.2/numbers/{number}")

    def move(self, number: str, body: NumberMoveRequest) -> NumberMoveData:
        return NumberMoveData.model_validate(
            unwrap(
                self._t.request("PATCH", f"/v2.2/numbers/{number}", json=body.to_payload())
            )
        )

    def release(self, number: str) -> None:
        """POST /v2.2/numbers/{number}/release — returns 204 No Content."""
        self._t.request("POST", f"/v2.2/numbers/{number}/release")

    def set_route(self, number: str, body: NumberRouteRequest) -> NumberRouteData:
        return NumberRouteData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/route", json=body.to_payload()
                )
            )
        )

    def set_translation(
        self, number: str, body: NumberTranslationRequest
    ) -> NumberTranslationData:
        return NumberTranslationData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/translation", json=body.to_payload()
                )
            )
        )

    def set_cnam(self, number: str, body: NumberCnamRequest) -> NumberCnamData:
        return NumberCnamData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/cnam", json=body.to_payload()
                )
            )
        )

    def set_lidb(self, number: str, body: NumberLidbRequest) -> NumberLidbData:
        return NumberLidbData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/lidb", json=body.to_payload()
                )
            )
        )

    def get_fax(self, number: str) -> NumberFaxData:
        return NumberFaxData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/numbers/{number}/fax"))
        )

    def set_fax(self, number: str, body: NumberFaxRequest) -> NumberFaxData:
        return NumberFaxData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/fax", json=body.to_payload()
                )
            )
        )

    def remove_fax(self, number: str) -> None:
        self._t.request("DELETE", f"/v2.2/numbers/{number}/fax")

    def set_forward(self, number: str, body: NumberForwardRequest) -> NumberForwardData:
        return NumberForwardData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/forward", json=body.to_payload()
                )
            )
        )

    def remove_forward(self, number: str) -> None:
        self._t.request("DELETE", f"/v2.2/numbers/{number}/forward")

    def get_sms(self, number: str) -> NumberSmsData:
        return NumberSmsData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/numbers/{number}/sms"))
        )

    def set_sms(self, number: str, body: NumberSmsRequest) -> NumberSmsData:
        return NumberSmsData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/sms", json=body.to_payload()
                )
            )
        )

    def remove_sms(self, number: str) -> None:
        self._t.request("DELETE", f"/v2.2/numbers/{number}/sms")

    def get_messaging(self, number: str) -> NumberMessagingState:
        return NumberMessagingState.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/numbers/{number}/messaging"))
        )

    def patch_messaging(
        self, number: str, body: NumberMessagingPatchRequest
    ) -> NumberMessagingPatchData:
        return NumberMessagingPatchData.model_validate(
            unwrap(
                self._t.request(
                    "PATCH", f"/v2.2/numbers/{number}/messaging", json=body.to_payload()
                )
            )
        )

    def assign_campaign(
        self, number: str, body: NumberCampaignAssignRequest
    ) -> NumberMessagingCampaignAssignData:
        return NumberMessagingCampaignAssignData.model_validate(
            unwrap(
                self._t.request(
                    "PUT",
                    f"/v2.2/numbers/{number}/messaging-campaign",
                    json=body.to_payload(),
                )
            )
        )

    def unassign_campaign(self, number: str) -> NumberMessagingCampaignUnassignData:
        return NumberMessagingCampaignUnassignData.model_validate(
            unwrap(
                self._t.request("DELETE", f"/v2.2/numbers/{number}/messaging-campaign")
            )
        )

    def bulk_unassign_campaign(
        self, numbers: Sequence[str]
    ) -> NumbersMessagingCampaignUnassignData:
        return NumbersMessagingCampaignUnassignData.model_validate(
            unwrap(
                self._t.request(
                    "DELETE",
                    "/v2.2/numbers/messaging-campaign",
                    json={"numbers": list(numbers)},
                )
            )
        )

    def set_port_out_pin(
        self, number: str, body: PortOutPinUpdateRequest
    ) -> PortOutPinUpdateData:
        return PortOutPinUpdateData.model_validate(
            unwrap(
                self._t.request(
                    "PATCH", f"/v2.2/numbers/{number}/port-out-pin", json=body.to_payload()
                )
            )
        )


class NumbersAsyncResource(AsyncResource):
    async def list(self) -> NumbersListData:
        return NumbersListData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/numbers"))
        )

    async def add(self, body: NumberAddRequest) -> NumberAddData:
        return NumberAddData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/numbers", json=body.to_payload()))
        )

    async def get(self, number: str) -> NumberDetail:
        return NumberDetail.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}"))
        )

    async def remove(self, number: str) -> None:
        await self._t.request("DELETE", f"/v2.2/numbers/{number}")

    async def move(self, number: str, body: NumberMoveRequest) -> NumberMoveData:
        return NumberMoveData.model_validate(
            unwrap(
                await self._t.request(
                    "PATCH", f"/v2.2/numbers/{number}", json=body.to_payload()
                )
            )
        )

    async def release(self, number: str) -> None:
        await self._t.request("POST", f"/v2.2/numbers/{number}/release")

    async def set_route(self, number: str, body: NumberRouteRequest) -> NumberRouteData:
        return NumberRouteData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/route", json=body.to_payload()
                )
            )
        )

    async def set_translation(
        self, number: str, body: NumberTranslationRequest
    ) -> NumberTranslationData:
        return NumberTranslationData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/translation", json=body.to_payload()
                )
            )
        )

    async def set_cnam(self, number: str, body: NumberCnamRequest) -> NumberCnamData:
        return NumberCnamData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/cnam", json=body.to_payload()
                )
            )
        )

    async def set_lidb(self, number: str, body: NumberLidbRequest) -> NumberLidbData:
        return NumberLidbData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/lidb", json=body.to_payload()
                )
            )
        )

    async def get_fax(self, number: str) -> NumberFaxData:
        return NumberFaxData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}/fax"))
        )

    async def set_fax(self, number: str, body: NumberFaxRequest) -> NumberFaxData:
        return NumberFaxData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/fax", json=body.to_payload()
                )
            )
        )

    async def remove_fax(self, number: str) -> None:
        await self._t.request("DELETE", f"/v2.2/numbers/{number}/fax")

    async def set_forward(
        self, number: str, body: NumberForwardRequest
    ) -> NumberForwardData:
        return NumberForwardData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/forward", json=body.to_payload()
                )
            )
        )

    async def remove_forward(self, number: str) -> None:
        await self._t.request("DELETE", f"/v2.2/numbers/{number}/forward")

    async def get_sms(self, number: str) -> NumberSmsData:
        return NumberSmsData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}/sms"))
        )

    async def set_sms(self, number: str, body: NumberSmsRequest) -> NumberSmsData:
        return NumberSmsData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/numbers/{number}/sms", json=body.to_payload()
                )
            )
        )

    async def remove_sms(self, number: str) -> None:
        await self._t.request("DELETE", f"/v2.2/numbers/{number}/sms")

    async def get_messaging(self, number: str) -> NumberMessagingState:
        return NumberMessagingState.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/numbers/{number}/messaging"))
        )

    async def patch_messaging(
        self, number: str, body: NumberMessagingPatchRequest
    ) -> NumberMessagingPatchData:
        return NumberMessagingPatchData.model_validate(
            unwrap(
                await self._t.request(
                    "PATCH", f"/v2.2/numbers/{number}/messaging", json=body.to_payload()
                )
            )
        )

    async def assign_campaign(
        self, number: str, body: NumberCampaignAssignRequest
    ) -> NumberMessagingCampaignAssignData:
        return NumberMessagingCampaignAssignData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT",
                    f"/v2.2/numbers/{number}/messaging-campaign",
                    json=body.to_payload(),
                )
            )
        )

    async def unassign_campaign(
        self, number: str
    ) -> NumberMessagingCampaignUnassignData:
        return NumberMessagingCampaignUnassignData.model_validate(
            unwrap(
                await self._t.request(
                    "DELETE", f"/v2.2/numbers/{number}/messaging-campaign"
                )
            )
        )

    async def bulk_unassign_campaign(
        self, numbers: Sequence[str]
    ) -> NumbersMessagingCampaignUnassignData:
        return NumbersMessagingCampaignUnassignData.model_validate(
            unwrap(
                await self._t.request(
                    "DELETE",
                    "/v2.2/numbers/messaging-campaign",
                    json={"numbers": list(numbers)},
                )
            )
        )

    async def set_port_out_pin(
        self, number: str, body: PortOutPinUpdateRequest
    ) -> PortOutPinUpdateData:
        return PortOutPinUpdateData.model_validate(
            unwrap(
                await self._t.request(
                    "PATCH", f"/v2.2/numbers/{number}/port-out-pin", json=body.to_payload()
                )
            )
        )
