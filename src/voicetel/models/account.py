"""Account-resource models — requests, response data payloads, and supporting entities."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from ._base import _Base

# ---------------------------------------------------------- shared subtypes ---


CallerIdPattern = r"^[2-9][0-9]{2}[2-9][0-9]{2}[0-9]{4}$"


class AccountRates(_Base):
    """Per-service rates on an account. Read-only for non-administrators."""

    cnam: float | None = Field(default=None, description="Per CNAM lookup, USD.")
    intlMax: float | None = Field(default=None, description="International call cap, USD/min.")
    nibble: float | None = Field(default=None, description="Domestic per-minute, USD/min.")
    lrn: float | None = Field(default=None, description="Per LRN lookup, USD.")
    fax: float | None = Field(default=None, description="Per fax page, USD.")
    tfAdj: float | None = Field(default=None, description="Toll-free adjustment, USD/min.")
    did: float | None = Field(default=None, description="Per DID per month, USD.")
    mms: float | None = Field(default=None, description="Per MMS, USD.")
    sms: float | None = Field(default=None, description="Per SMS, USD.")


class AccountServices(_Base):
    """Per-service feature flags. ``true`` = enabled on this account."""

    e911: bool | None = None
    cnam: bool | None = Field(default=None, description="Inbound CNAM lookups enabled.")
    bypassMedia: bool | None = None
    intl: bool | None = Field(default=None, description="International calling enabled.")
    rcid: bool | None = Field(default=None, description="Remote Caller ID display enabled.")
    mms: bool | None = None
    dialer: bool | None = None
    sms: bool | None = None


class CreditEntry(_Base):
    """A single credit row in :class:`AccountCreditsData`."""

    date: str = Field(description="ISO 8601 timestamp the credit was applied.")
    paid: bool = Field(description="True = invoice has been paid; False = still outstanding.")
    amount: float = Field(description="Credit amount in USD.")


PaymentStatus = Literal[
    "Completed", "Pending", "Reversed", "Refunded", "Failed", "Denied", "Canceled_Reversal"
]


class PaymentEntry(_Base):
    """A single payment row in :class:`AccountPaymentsData`."""

    transactionId: str | None = Field(default=None, description="PayPal transaction ID.")
    date: str = Field(description="ISO 8601 timestamp of the payment.")
    payerEmail: str | None = Field(default=None, description="PayPal email of the payer.")
    status: PaymentStatus
    amount: float = Field(description="Payment amount in USD.")


class CdrEntryValue(_Base):
    """Per-call billing summary inside a CDR row.

    All numeric-looking fields (``dur``, ``ba``, ``nr``) are intentionally strings to preserve
    exact precision on the wire. Use :class:`decimal.Decimal` for math.
    """

    dur: str | None = Field(default=None, description="Billed duration in seconds.")
    dst: str | None = Field(default=None, description="Destination (called party) TN.")
    ba: str | None = Field(default=None, description="Billed amount, USD.")
    nr: str | None = Field(default=None, description="Nibble rate, USD/min.")
    cn: str | None = Field(default=None, description="URL-encoded display name (CNAM at call time).")
    ip: str | None = Field(default=None, description="IPv4 of the leg.")
    cid: str | None = Field(default=None, description="Caller ID (calling party) TN.")


class CdrEntry(_Base):
    """A single CDR row."""

    id: str = Field(description="Stable record identifier for the call.")
    key: list[str] = Field(
        min_length=2,
        max_length=2,
        description="Composite key — [accountUsername, startEpochUnixSeconds], both strings.",
    )
    value: CdrEntryValue


class MrcCharge(_Base):
    """A single monthly-recurring charge row inside :class:`AccountMrcData`."""

    amount: float = Field(description="Charge amount in USD.")
    description: str | None = Field(default=None, description="Charge description.")


# ----------------------------------------------------------------- requests ---


class AccountAddRequest(_Base):
    """POST /v2.2/account — admin-only sub-account creation."""

    username: int = Field(description="10-digit numeric username for the new sub-account.")
    name: str = Field(description="Human-readable account name.")
    email: str = Field(description="Account email.")
    masterAccount: int | None = Field(
        default=None,
        description="Billing account. Defaults to ``username``.",
    )


class AccountPutRequest(_Base):
    """PUT /v2.2/account — update account settings."""

    notify: bool | None = None
    notifyThreshold: int | None = None
    timezone: str | None = None
    callerId: Annotated[str, Field(pattern=CallerIdPattern)] | None = None
    e911: bool | None = Field(default=None, description="Admin only.")
    intl: bool | None = Field(default=None, description="Admin only.")
    sms: bool | None = Field(default=None, description="Admin only.")
    mms: bool | None = Field(default=None, description="Admin only.")
    ccs: int | None = Field(default=None, description="Admin only; concurrent-call cap.")


class AccountSignupRequest(_Base):
    """POST /v2.2/accounts — public sign-up."""

    name: str
    email: str
    promo: str | None = Field(default=None, description="Optional promotional code.")


class AccountRecoverRequest(_Base):
    """POST /v2.2/account/recovery — password recovery (no auth required)."""

    email: str


class ApiKeyRequest(_Base):
    """POST /v2.2/account/api-key — exchange username/password for a bearer token.

    No auth required for this endpoint. Subject to the 6 req/hour/IP rate limit shared by
    ``account/cdr``, ``account/recurring-charges``, ``account/payments``, ``account/registration``,
    and this endpoint.
    """

    username: int
    password: str


# ------------------------------------------------------- response data shapes ---


class AccountAddData(_Base):
    """Data payload from POST /v2.2/account (admin create)."""

    password: str | None = Field(default=None, description="Auto-generated initial password.")
    email: str | None = None
    masterAccount: str | None = None
    username: str | None = Field(default=None, description="The new account's identifier.")
    name: str | None = None


class AccountApiKeyData(_Base):
    """Data payload from POST /v2.2/account/api-key."""

    apikey: str = Field(description="32-hex bearer token.")


class AccountCdrData(_Base):
    """Data payload from GET /v2.2/account/cdr."""

    cdr: list[CdrEntry] = Field(description="Newest-first call records in the requested range.")
    start: int = Field(description="Echo of the `start` query parameter (Unix seconds).")
    end: int = Field(description="Echo of the `end` query parameter (Unix seconds).")


class AccountCreditsData(_Base):
    """Data payload from GET /v2.2/account/credits."""

    credits: list[CreditEntry] = Field(description="Full credit history, newest first.")


class AccountData(_Base):
    """Data payload from GET /v2.2/account — the authenticated account's profile."""

    username: str | None = Field(default=None, description="Account identifier.")
    name: str | None = Field(default=None, description="Human-readable name.")
    email: str | None = None
    enabled: bool | None = None
    created: str | None = Field(default=None, description="ISO 8601 creation timestamp.")
    cash: float | None = Field(default=None, description="Current balance, USD.")
    callerId: str | None = Field(
        default=None,
        description="Default outbound caller ID — 10-digit TN.",
    )
    timezone: str | None = Field(default=None, description="IANA timezone identifier.")
    authType: int | None = Field(default=None, description="Authentication mode.")
    ccs: int | None = Field(default=None, description="Max concurrent calls.")
    notify: bool | None = None
    notifyThreshold: int | None = Field(
        default=None,
        description="Balance threshold (USD) below which notifications fire.",
    )
    rates: AccountRates | None = None
    services: AccountServices | None = None


class AccountMrcData(_Base):
    """Data payload from GET /v2.2/account/recurring-charges."""

    charges: list[MrcCharge] = Field(description="Active recurring charges.")
    total: float = Field(description="Sum of all charges, USD.")


class AccountPaymentsData(_Base):
    """Data payload from GET /v2.2/account/payments."""

    payments: list[PaymentEntry] = Field(description="Full payment history, newest first.")


class AccountPutData(_Base):
    """Data payload from PUT /v2.2/account."""

    updated: list[str] = Field(description="Names of fields that were updated.")


class AccountRecoverData(_Base):
    """Data payload from POST /v2.2/account/recovery."""

    message: str | None = Field(default=None, description="Confirmation message.")


class AccountRegistrationData(_Base):
    """Data payload from GET /v2.2/account/registration — current SIP registration."""

    agent: str | None = Field(default=None, description="SIP User-Agent string.")
    uri: str | None = Field(default=None, description="SIP URI of the registered endpoint.")
    expires: int | None = Field(default=None, description="Seconds until the registration expires.")


class AccountSignupData(_Base):
    """Data payload from POST /v2.2/accounts (public sign-up)."""

    username: str | None = None
    name: str | None = None
    email: str | None = None
    password: str | None = Field(default=None, description="Auto-generated initial password.")
