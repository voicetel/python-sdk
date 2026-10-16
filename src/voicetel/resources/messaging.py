from __future__ import annotations

from typing import Any, Literal

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

    def health(self) -> Any:
        """GET /v2.2/messaging/health — account-wide messaging health overview.

        Mirrors the portal Messaging tab: summary counts (numbers, messaging on, healthy,
        needing attention, in progress), campaigns with carrier-review progress, numbers
        needing attention (each with a plain-language title, detail and fix-it actions),
        14 days of delivery counts, and the alert-email setting. Updated hourly.

        The spec defines no response schema for this endpoint, so the decoded JSON payload
        is returned as-is.
        """
        return unwrap(self._t.request("GET", "/v2.2/messaging/health"))

    def health_alerts(self) -> Any:
        """GET /v2.2/messaging/health/alerts — the alert-email setting.

        Whether new messaging problems are emailed to the account. The spec defines no
        response schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(self._t.request("GET", "/v2.2/messaging/health/alerts"))

    def set_health_alerts(self, *, enabled: bool) -> Any:
        """PUT /v2.2/messaging/health/alerts — turn alert emails on or off.

        The account is emailed when new messaging problems are found (at most one digest
        about every 20 hours). The spec defines no response schema, so the decoded JSON
        payload is returned as-is.
        """
        return unwrap(
            self._t.request("PUT", "/v2.2/messaging/health/alerts", json={"enabled": enabled})
        )

    def health_check(self, *, number: str) -> Any:
        """POST /v2.2/messaging/health/check — live health check of one number.

        Reports in-service, messaging enabled, campaign approved, assignment by the
        messaging provider, delivery failures in the last 24 hours, and enablement in
        progress. Limited to 30 checks per hour per account. The spec defines no response
        schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(
            self._t.request("POST", "/v2.2/messaging/health/check", json={"number": number})
        )

    def health_samples(self, *, number: str) -> Any:
        """GET /v2.2/messaging/health/samples — recent messages blocked as spam.

        Up to 3 recent outbound messages from ``number`` that carriers blocked as spam
        (time, masked recipient, text, reason), to help review content. The spec defines no
        response schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(
            self._t.request("GET", "/v2.2/messaging/health/samples", params={"number": number})
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

    async def health(self) -> Any:
        """GET /v2.2/messaging/health — account-wide messaging health overview.

        The spec defines no response schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(await self._t.request("GET", "/v2.2/messaging/health"))

    async def health_alerts(self) -> Any:
        """GET /v2.2/messaging/health/alerts — the alert-email setting.

        The spec defines no response schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(await self._t.request("GET", "/v2.2/messaging/health/alerts"))

    async def set_health_alerts(self, *, enabled: bool) -> Any:
        """PUT /v2.2/messaging/health/alerts — turn alert emails on or off.

        The spec defines no response schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(
            await self._t.request(
                "PUT", "/v2.2/messaging/health/alerts", json={"enabled": enabled}
            )
        )

    async def health_check(self, *, number: str) -> Any:
        """POST /v2.2/messaging/health/check — live health check of one number.

        Limited to 30 checks per hour per account. The spec defines no response schema, so
        the decoded JSON payload is returned as-is.
        """
        return unwrap(
            await self._t.request(
                "POST", "/v2.2/messaging/health/check", json={"number": number}
            )
        )

    async def health_samples(self, *, number: str) -> Any:
        """GET /v2.2/messaging/health/samples — recent messages blocked as spam.

        The spec defines no response schema, so the decoded JSON payload is returned as-is.
        """
        return unwrap(
            await self._t.request(
                "GET", "/v2.2/messaging/health/samples", params={"number": number}
            )
        )
