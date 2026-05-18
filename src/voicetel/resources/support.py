from __future__ import annotations

from ..models import (
    TicketCreateRequest,
    TicketData,
    TicketReplyData,
    TicketReplyRequest,
    TicketsListData,
    TicketThreadsData,
    TicketUpdateData,
    TicketUpdateRequest,
)
from ._base import AsyncResource, Resource, unwrap


class SupportResource(Resource):
    """Support tickets."""

    def list(self) -> TicketsListData:
        return TicketsListData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/support/tickets"))
        )

    def create(self, body: TicketCreateRequest) -> TicketData:
        return TicketData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/support/tickets", json=body.to_payload()))
        )

    def get(self, ticket_id: int) -> TicketData:
        return TicketData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}"))
        )

    def update(self, ticket_id: int, body: TicketUpdateRequest) -> TicketUpdateData:
        return TicketUpdateData.model_validate(
            unwrap(
                self._t.request(
                    "PUT", f"/v2.2/support/tickets/{ticket_id}", json=body.to_payload()
                )
            )
        )

    def delete(self, ticket_id: int) -> None:
        """DELETE /v2.2/support/tickets/{id} — admin only; returns 204 No Content."""
        self._t.request("DELETE", f"/v2.2/support/tickets/{ticket_id}")

    def messages(self, ticket_id: int) -> TicketThreadsData:
        return TicketThreadsData.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}/messages"))
        )

    def reply(self, ticket_id: int, body: TicketReplyRequest) -> TicketReplyData:
        return TicketReplyData.model_validate(
            unwrap(
                self._t.request(
                    "POST",
                    f"/v2.2/support/tickets/{ticket_id}/replies",
                    json=body.to_payload(),
                )
            )
        )


class SupportAsyncResource(AsyncResource):
    async def list(self) -> TicketsListData:
        return TicketsListData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/support/tickets"))
        )

    async def create(self, body: TicketCreateRequest) -> TicketData:
        return TicketData.model_validate(
            unwrap(
                await self._t.request("POST", "/v2.2/support/tickets", json=body.to_payload())
            )
        )

    async def get(self, ticket_id: int) -> TicketData:
        return TicketData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}"))
        )

    async def update(self, ticket_id: int, body: TicketUpdateRequest) -> TicketUpdateData:
        return TicketUpdateData.model_validate(
            unwrap(
                await self._t.request(
                    "PUT", f"/v2.2/support/tickets/{ticket_id}", json=body.to_payload()
                )
            )
        )

    async def delete(self, ticket_id: int) -> None:
        await self._t.request("DELETE", f"/v2.2/support/tickets/{ticket_id}")

    async def messages(self, ticket_id: int) -> TicketThreadsData:
        return TicketThreadsData.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}/messages"))
        )

    async def reply(self, ticket_id: int, body: TicketReplyRequest) -> TicketReplyData:
        return TicketReplyData.model_validate(
            unwrap(
                await self._t.request(
                    "POST",
                    f"/v2.2/support/tickets/{ticket_id}/replies",
                    json=body.to_payload(),
                )
            )
        )
