from __future__ import annotations

from typing import Any

from ..models import (
    AccountAddRequest,
    AccountPutRequest,
    AccountRecoverRequest,
    AccountSignupRequest,
)
from ._base import AsyncResource, Resource, unwrap


class AccountResource(Resource):
    """Operations under the ``Account`` tag.

    Note: ``cdr``, ``credits``, ``recurring_charges``, ``payments``, ``registration`` and
    ``api_key`` share a 6 req/hour/IP rate limit. Bursting will trigger 429s.
    """

    def get(self) -> Any:
        """GET /v2.2/account — current account info."""
        return unwrap(self._t.request("GET", "/v2.2/account"))

    def update(self, body: AccountPutRequest) -> Any:
        """PUT /v2.2/account — update account settings."""
        return unwrap(self._t.request("PUT", "/v2.2/account", json=body.to_payload()))

    def add(self, body: AccountAddRequest) -> Any:
        """POST /v2.2/account — create a sub-account (admin only)."""
        return unwrap(self._t.request("POST", "/v2.2/account", json=body.to_payload()))

    def list(self) -> Any:
        """POST /v2.2/accounts — list sub-accounts the caller can see."""
        return unwrap(self._t.request("POST", "/v2.2/accounts"))

    def signup(self, body: AccountSignupRequest) -> Any:
        """POST /v2.2/accounts — public sign-up flow."""
        return unwrap(self._t.request("POST", "/v2.2/accounts", json=body.to_payload()))

    def cdr(self, *, start: int | None = None, end: int | None = None) -> Any:
        """GET /v2.2/account/cdr — call detail records.

        ``start`` and ``end`` are Unix timestamps. Rate-limited (6/hr/IP).
        """
        return unwrap(
            self._t.request("GET", "/v2.2/account/cdr", params={"start": start, "end": end})
        )

    def credits(self) -> Any:
        """GET /v2.2/account/credits — credit/payment history."""
        return unwrap(self._t.request("GET", "/v2.2/account/credits"))

    def recurring_charges(self) -> Any:
        """GET /v2.2/account/recurring-charges — monthly recurring charges (MRC)."""
        return unwrap(self._t.request("GET", "/v2.2/account/recurring-charges"))

    def payments(self) -> Any:
        """GET /v2.2/account/payments — payment history."""
        return unwrap(self._t.request("GET", "/v2.2/account/payments"))

    def registration(self) -> Any:
        """GET /v2.2/account/registration — SIP registration."""
        return unwrap(self._t.request("GET", "/v2.2/account/registration"))

    def recover(self, body: AccountRecoverRequest) -> Any:
        """POST /v2.2/account/recovery — start password recovery (no auth required)."""
        return unwrap(
            self._t.request(
                "POST",
                "/v2.2/account/recovery",
                json=body.to_payload(),
                require_auth=False,
            )
        )


class AccountAsyncResource(AsyncResource):
    """Async counterpart of :class:`AccountResource`."""

    async def get(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/account"))

    async def update(self, body: AccountPutRequest) -> Any:
        return unwrap(await self._t.request("PUT", "/v2.2/account", json=body.to_payload()))

    async def add(self, body: AccountAddRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/account", json=body.to_payload()))

    async def list(self) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/accounts"))

    async def signup(self, body: AccountSignupRequest) -> Any:
        return unwrap(await self._t.request("POST", "/v2.2/accounts", json=body.to_payload()))

    async def cdr(
        self, *, start: int | None = None, end: int | None = None
    ) -> Any:
        return unwrap(
            await self._t.request(
                "GET", "/v2.2/account/cdr", params={"start": start, "end": end}
            )
        )

    async def credits(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/account/credits"))

    async def recurring_charges(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/account/recurring-charges"))

    async def payments(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/account/payments"))

    async def registration(self) -> Any:
        return unwrap(await self._t.request("GET", "/v2.2/account/registration"))

    async def recover(self, body: AccountRecoverRequest) -> Any:
        return unwrap(
            await self._t.request(
                "POST",
                "/v2.2/account/recovery",
                json=body.to_payload(),
                require_auth=False,
            )
        )
