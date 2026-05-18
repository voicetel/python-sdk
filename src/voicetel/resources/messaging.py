from __future__ import annotations

from typing import Any

from ..models import (
    MessageSendRequest,
    MessagingBrandCreateRequest,
    MessagingCampaignCreateRequest,
)
from ._base import AsyncResource, Resource, unwrap


class MessagingResource(Resource):
    """SMS/MMS and 10DLC brand/campaign registration."""

    def history(
        self, *, number: str | None = None, start: int | None = None, end: int | None = None
    ) -> Any:
        """GET /v2.2/messages — message history."""
        return unwrap(
            self._t.request(
                "GET", "/v2.2/messages", params={"number": number, "start": start, "end": end}
            )
        )

    def send(self, body: MessageSendRequest) -> Any:
        """POST /v2.2/messages — send SMS or MMS (MMS if ``mediaUrls`` is set)."""
        return unwrap(self._t.request("POST", "/v2.2/messages", json=body.to_payload()))

    def brands(self, body: MessagingBrandCreateRequest) -> Any:
        """POST /v2.2/messaging/brands — register a 10DLC brand."""
        return unwrap(
            self._t.request("POST", "/v2.2/messaging/brands", json=body.to_payload())
        )

    def campaign_status(self) -> Any:
        """GET /v2.2/messaging/campaigns — current 10DLC campaign statuses."""
        return unwrap(self._t.request("GET", "/v2.2/messaging/campaigns"))

    def campaign_create(self, body: MessagingCampaignCreateRequest) -> Any:
        """POST /v2.2/messaging/campaigns — register a 10DLC campaign."""
        return unwrap(
            self._t.request("POST", "/v2.2/messaging/campaigns", json=body.to_payload())
        )

    def numbers_state(self, *, numbers: list[str] | None = None) -> Any:
        """GET /v2.2/numbers/messaging — messaging state for many numbers at once."""
        params: dict[str, Any] = {}
        if numbers is not None:
            params["numbers"] = ",".join(numbers)
        return unwrap(self._t.request("GET", "/v2.2/numbers/messaging", params=params))


class MessagingAsyncResource(AsyncResource):
    async def history(
        self, *, number: str | None = None, start: int | None = None, end: int | None = None
    ) -> Any:
        return unwrap(
            await self._t.request(
                "GET", "/v2.2/messages", params={"number": number, "start": start, "end": end}
            )
        )

    async def send(self, body: MessageSendRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/messages", json=body.to_payload()))

    async def brands(self, body: MessagingBrandCreateRequest) -> Any:
        return unwrap(
            await self._t.request("POST", "/v2.2/messaging/brands", json=body.to_payload())
        )

    async def campaign_status(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/messaging/campaigns"))

    async def campaign_create(self, body: MessagingCampaignCreateRequest) -> Any:
        return unwrap(
            await self._t.request(
                "POST", "/v2.2/messaging/campaigns", json=body.to_payload()
            )
        )

    async def numbers_state(
        self, *, numbers: list[str] | None = None
    ) -> Any:
        params: dict[str, Any] = {}
        if numbers is not None:
            params["numbers"] = ",".join(numbers)
        return unwrap(await self._t.request("GET", "/v2.2/numbers/messaging", params=params))
