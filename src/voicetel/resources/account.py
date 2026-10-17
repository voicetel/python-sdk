from __future__ import annotations

from typing import Literal

from ..models import (
    AccountAddData,
    AccountAddRequest,
    AccountCdrData,
    AccountCreditsData,
    AccountData,
    AccountMrcData,
    AccountPaymentsData,
    AccountPutData,
    AccountPutRequest,
    AccountRecoverData,
    AccountRecoverRequest,
    AccountRegistrationData,
    AccountSignupData,
    AccountSignupRequest,
)
from ._base import AsyncResource, Resource, unwrap

CreditStatusFilter = Literal["paid", "unpaid"]


class AccountResource(Resource):
    """Operations under the ``Account`` tag.

    Note: ``get``, ``cdr``, ``recurring_charges`` and ``client.login()`` share a
    6 req/hour/IP rate limit. Bursting will trigger 429s.
    """

    def get(self) -> AccountData:
        """GET /v2.2/account — account profile. Rate-limited (6/hr/IP)."""
        return AccountData.model_validate(unwrap(self._t.request("GET", "/v2.2/account")))

    def update(self, body: AccountPutRequest) -> AccountPutData:
        return AccountPutData.model_validate(
            unwrap(self._t.request("PUT", "/v2.2/account", json=body.to_payload()))
        )

    def add(self, body: AccountAddRequest) -> AccountAddData:
        return AccountAddData.model_validate(
            unwrap(self._t.request("POST", "/v2.2/account", json=body.to_payload()))
        )

    def signup(self, body: AccountSignupRequest) -> AccountSignupData:
        """POST /v2.2/accounts — public sign-up flow (no auth required)."""
        return AccountSignupData.model_validate(
            unwrap(
                self._t.request(
                    "POST", "/v2.2/accounts", json=body.to_payload(), require_auth=False
                )
            )
        )

    def cdr(self, *, start: int | None = None, end: int | None = None) -> AccountCdrData:
        """GET /v2.2/account/cdr — call detail records. Rate-limited (6/hr/IP)."""
        return AccountCdrData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/account/cdr", params={"start": start, "end": end}))
        )

    def credits(self, *, status: CreditStatusFilter | None = None) -> AccountCreditsData:
        """GET /v2.2/account/credits — credit history. ``status`` filters paid/unpaid."""
        return AccountCreditsData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/account/credits", params={"status": status}))
        )

    def recurring_charges(self) -> AccountMrcData:
        """GET /v2.2/account/recurring-charges — MRC breakdown. Rate-limited (6/hr/IP)."""
        return AccountMrcData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/account/recurring-charges"))
        )

    def payments(self) -> AccountPaymentsData:
        return AccountPaymentsData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/account/payments"))
        )

    def registration(self) -> AccountRegistrationData:
        return AccountRegistrationData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/account/registration"))
        )

    def recover(self, body: AccountRecoverRequest) -> AccountRecoverData:
        """POST /v2.2/account/recovery — no auth required."""
        return AccountRecoverData.model_validate(
            unwrap(
                self._t.request(
                    "POST",
                    "/v2.2/account/recovery",
                    json=body.to_payload(),
                    require_auth=False,
                )
            )
        )


class AccountAsyncResource(AsyncResource):
    async def get(self) -> AccountData:
        """GET /v2.2/account — account profile. Rate-limited (6/hr/IP)."""
        return AccountData.model_validate(unwrap(await self._t.request("GET", "/v2.2/account")))

    async def update(self, body: AccountPutRequest) -> AccountPutData:
        return AccountPutData.model_validate(
            unwrap(await self._t.request("PUT", "/v2.2/account", json=body.to_payload()))
        )

    async def add(self, body: AccountAddRequest) -> AccountAddData:
        return AccountAddData.model_validate(
            unwrap(await self._t.request("POST", "/v2.2/account", json=body.to_payload()))
        )

    async def signup(self, body: AccountSignupRequest) -> AccountSignupData:
        """POST /v2.2/accounts — public sign-up flow (no auth required)."""
        return AccountSignupData.model_validate(
            unwrap(
                await self._t.request(
                    "POST", "/v2.2/accounts", json=body.to_payload(), require_auth=False
                )
            )
        )

    async def cdr(
        self, *, start: int | None = None, end: int | None = None
    ) -> AccountCdrData:
        """GET /v2.2/account/cdr — call detail records. Rate-limited (6/hr/IP)."""
        return AccountCdrData.model_validate(
            unwrap(
                await self._t.request(
                    "GET", "/v2.2/account/cdr", params={"start": start, "end": end}
                )
            )
        )

    async def credits(self, *, status: CreditStatusFilter | None = None) -> AccountCreditsData:
        """GET /v2.2/account/credits — credit history. ``status`` filters paid/unpaid."""
        return AccountCreditsData.model_validate(
            unwrap(
                await self._t.request("GET", "/v2.2/account/credits", params={"status": status})
            )
        )

    async def recurring_charges(self) -> AccountMrcData:
        """GET /v2.2/account/recurring-charges — MRC breakdown. Rate-limited (6/hr/IP)."""
        return AccountMrcData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/account/recurring-charges"))
        )

    async def payments(self) -> AccountPaymentsData:
        return AccountPaymentsData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/account/payments"))
        )

    async def registration(self) -> AccountRegistrationData:
        return AccountRegistrationData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/account/registration"))
        )

    async def recover(self, body: AccountRecoverRequest) -> AccountRecoverData:
        return AccountRecoverData.model_validate(
            unwrap(
                await self._t.request(
                    "POST",
                    "/v2.2/account/recovery",
                    json=body.to_payload(),
                    require_auth=False,
                )
            )
        )
