from __future__ import annotations

from typing import Literal

from ..models import (
    MessageHistoryData,
    MessageSendData,
    MessageSendRequest,
    MessagingBrandCreateData,
    MessagingBrandCreateRequest,
    MessagingCampaignCreateData,
    MessagingCampaignCreateRequest,
    MessagingCampaignStatusData,
    NumbersMessagingListData,
)
from ._base import AsyncResource, Resource, unwrap

MessageHistoryQueryType = Literal["sms", "mms", "dlr"]


class MessagingResource(Resource):
    """SMS/MMS and 10DLC brand/campaign registration."""

    def history(
        self,
        *,
        number: str | None = None,
        start: int | None = None,
        end: int | None = None,
        type: MessageHistoryQueryType | None = None,
    ) -> MessageHistoryData:
        return MessageHistoryData.model_validate(
            unwrap(
                self._t.request(
                    "GET",
                    "/v2.2/messages",
                    params={"number": number, "start": start, "end": end, "type": type},
                )
            )
        )

    def send(self, body: MessageSendRequest) -> MessageSendData:
        return MessageSendData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/messages", json=body.to_payload()))
        )

    def brands(self, body: MessagingBrandCreateRequest) -> MessagingBrandCreateData:
        return MessagingBrandCreateData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/messaging/brands", json=body.to_payload()))
        )

    def campaign_status(self) -> MessagingCampaignStatusData:
        return MessagingCampaignStatusData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/messaging/campaigns"))
        )

    def campaign_create(
        self, body: MessagingCampaignCreateRequest
    ) -> MessagingCampaignCreateData:
        return MessagingCampaignCreateData.model_validate(
            unwrap(
                self._t.request("POST", "/v2.2/messaging/campaigns", json=body.to_payload())
            )
        )

    def numbers_state(self, *, numbers: list[str] | None = None) -> NumbersMessagingListData:
        params: dict[str, str] = {}
        if numbers is not None:
            params["numbers"] = ",".join(numbers)
        return NumbersMessagingListData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/numbers/messaging", params=params))
        )


class MessagingAsyncResource(AsyncResource):
    async def history(
        self,
        *,
        number: str | None = None,
        start: int | None = None,
        end: int | None = None,
        type: MessageHistoryQueryType | None = None,
    ) -> MessageHistoryData:
        return MessageHistoryData.model_validate(
            unwrap(
                await self._t.request(
                    "GET",
                    "/v2.2/messages",
                    params={"number": number, "start": start, "end": end, "type": type},
                )
            )
        )

    async def send(self, body: MessageSendRequest) -> MessageSendData:
        return MessageSendData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/messages", json=body.to_payload()))
        )

    async def brands(self, body: MessagingBrandCreateRequest) -> MessagingBrandCreateData:
        return MessagingBrandCreateData.model_validate(
            unwrap(
                await self._t.request(
                    "POST", "/v2.2/messaging/brands", json=body.to_payload()
                )
            )
        )

    async def campaign_status(self) -> MessagingCampaignStatusData:
        return MessagingCampaignStatusData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/messaging/campaigns"))
        )

    async def campaign_create(
        self, body: MessagingCampaignCreateRequest
    ) -> MessagingCampaignCreateData:
        return MessagingCampaignCreateData.model_validate(
            unwrap(
                await self._t.request(
                    "POST", "/v2.2/messaging/campaigns", json=body.to_payload()
                )
            )
        )

    async def numbers_state(
        self, *, numbers: list[str] | None = None
    ) -> NumbersMessagingListData:
        params: dict[str, str] = {}
        if numbers is not None:
            params["numbers"] = ",".join(numbers)
        return NumbersMessagingListData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/numbers/messaging", params=params))
        )
