from __future__ import annotations

from typing import Any

from ..models import TicketCreateRequest, TicketReplyRequest, TicketUpdateRequest
from ._base import AsyncResource, Resource, unwrap


class SupportResource(Resource):
    """Support tickets."""

    def list(self) -> Any:
        """GET /v2.2/support/tickets"""
        return unwrap(self._t.request("GET", "/v2.2/support/tickets"))

    def create(self, body: TicketCreateRequest) -> Any:
        """POST /v2.2/support/tickets"""
        return unwrap(
            self._t.request("POST", "/v2.2/support/tickets", json=body.to_payload())
        )

    def get(self, ticket_id: int) -> Any:
        return unwrap(self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}"))

    def update(self, ticket_id: int, body: TicketUpdateRequest) -> Any:
        return unwrap(
            self._t.request(
                "PUT", f"/v2.2/support/tickets/{ticket_id}", json=body.to_payload()
            )
        )

    def delete(self, ticket_id: int) -> Any:
        """Admin only."""
        return unwrap(self._t.request("DELETE", f"/v2.2/support/tickets/{ticket_id}"))

    def messages(self, ticket_id: int) -> Any:
        return unwrap(
            self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}/messages")
        )

    def reply(self, ticket_id: int, body: TicketReplyRequest) -> Any:
        return unwrap(
            self._t.request(
                "POST", f"/v2.2/support/tickets/{ticket_id}/replies", json=body.to_payload()
            )
        )


class SupportAsyncResource(AsyncResource):
    async def list(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/support/tickets"))

    async def create(self, body: TicketCreateRequest) -> Any:
        return unwrap(
            await self._t.request("POST", "/v2.2/support/tickets", json=body.to_payload())
        )

    async def get(self, ticket_id: int) -> Any:
        return unwrap(await self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}"))

    async def update(self, ticket_id: int, body: TicketUpdateRequest) -> Any:
        return unwrap(
            await self._t.request(
                "PUT", f"/v2.2/support/tickets/{ticket_id}", json=body.to_payload()
            )
        )

    async def delete(self, ticket_id: int) -> Any:
        return unwrap(await self._t.request("DELETE", f"/v2.2/support/tickets/{ticket_id}"))

    async def messages(self, ticket_id: int) -> Any:
        return unwrap(
            await self._t.request("GET", f"/v2.2/support/tickets/{ticket_id}/messages")
        )

    async def reply(self, ticket_id: int, body: TicketReplyRequest) -> Any:
        return unwrap(
            await self._t.request(
                "POST", f"/v2.2/support/tickets/{ticket_id}/replies", json=body.to_payload()
            )
        )
