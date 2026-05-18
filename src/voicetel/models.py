"""Pydantic models for VoiceTel API v2.2.6 request and response payloads.

Naming: request bodies are ``*Request`` (e.g. :class:`NumberAddRequest`); response data shapes
(the inner ``data`` field of the response envelope) are named after the resource
(:class:`NumberDetail`, :class:`Ticket`, :class:`GatewayEntry`).

Every model allows extra fields on the way *in* (the server is allowed to add fields without
breaking clients) and serializes only the set fields on the way *out* (so PATCH/PUT bodies don't
send ``None`` for every unspecified field).
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PhoneNumber = Annotated[str, Field(pattern=r"^[0-9]{10}$")]


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    def to_payload(self) -> dict[str, Any]:
        """Render as JSON-ready dict, omitting fields the user never set."""
        return self.model_dump(exclude_unset=True, by_alias=True, mode="json")


# ---------------------------------------------------------------- Account ---


class AccountAddRequest(_Base):
    username: int = Field(description="10-digit numeric username for the new sub-account.")
    name: str
    email: str
    masterAccount: int | None = Field(
        default=None, description="Billing account; defaults to ``username``."
    )


class AccountPutRequest(_Base):
    notify: bool | None = None
    notifyThreshold: int | None = None
    timezone: str | None = None
    callerId: str | None = None
    e911: bool | None = Field(default=None, description="Admin only.")
    intl: bool | None = Field(default=None, description="Admin only.")
    sms: bool | None = Field(default=None, description="Admin only.")
    mms: bool | None = Field(default=None, description="Admin only.")
    ccs: int | None = Field(default=None, description="Admin only; concurrent-call cap.")


class AccountSignupRequest(_Base):
    name: str
    email: str
    promo: str | None = None


class AccountRecoverRequest(_Base):
    email: str


class ApiKeyRequest(_Base):
    username: int
    password: str


# -------------------------------------------------------------------- ACL ---


class CidrEntry(_Base):
    cidr: str


class AclModifyRequest(_Base):
    acl: list[CidrEntry]


# ------------------------------------------------------------------- Auth ---


AuthType = Literal[0, 1, 2, 3]


class AuthPutRequest(_Base):
    authType: AuthType | None = None
    password: str | None = Field(
        default=None,
        description="6-10 alphanumeric chars with at least one letter and one number.",
    )


# ---------------------------------------------------------------- E911 ---


class E911CreateRequest(_Base):
    dn: PhoneNumber
    callername: str
    address1: str
    address2: str | None = None
    city: str
    state: str
    zip: str


class E911AddressRequest(_Base):
    address1: str
    address2: str | None = None
    city: str
    state: str
    zip: str


class E911ProvisionByIdRequest(_Base):
    callername: str
    addressid: int


# ------------------------------------------------------------- Gateways ---


class GatewayAddRequest(_Base):
    gateway: str = Field(
        description=(
            "IP or hostname with optional ``:port``; "
            "must resolve to a routable public IPv4."
        )
    )
    prefix: str | None = Field(default=None, description="Digits to prepend on outbound calls.")
    limit: int | None = Field(
        default=None, ge=1, le=1000, description="Max concurrent calls. Default: 23."
    )


class GatewayUpdateRequest(_Base):
    gateway: str | None = None
    prefix: str | None = None
    limit: int | None = Field(default=None, ge=1, le=1000)


# ----------------------------------------------------------------- Numbers ---


class NumberAddRequest(_Base):
    number: int
    route: int | None = Field(default=None, description="Gateway route ID; defaults to 4 (DID).")


class NumberRouteRequest(_Base):
    route: int


class NumberCnamRequest(_Base):
    enabled: bool


class NumberLibdRequest(_Base):
    cnam: str = Field(description="Outbound caller name. Max 15 alphanumeric characters.")
    customerOrderReference: str | None = None


class NumberFaxRequest(_Base):
    email: str


class NumberForwardRequest(_Base):
    destination: int


class NumberTranslationRequest(_Base):
    translation: str = Field(description="DNIS translation. Digits and # only.")


class NumberSmsRequest(_Base):
    type: Literal["email", "webhook", "sip"]
    resource: str


class NumberMessagingPatchRequest(_Base):
    routeIn: int | None = None
    routeOut: int | None = None


class NumberCampaignAssignRequest(_Base):
    campaignId: Annotated[str, Field(pattern=r"^[A-Z0-9]+$")]


class NumberMoveRequest(_Base):
    accountId: int
    route: int


class PortOutPinUpdateRequest(_Base):
    pin: Annotated[str, Field(pattern=r"^[0-9]{4}$")]


# --------------------------------------------------------------- Messaging ---


class MessageSendRequest(_Base):
    from_: PhoneNumber = Field(alias="from")
    to: PhoneNumber
    text: str
    subject: str | None = Field(default=None, description="MMS subject (MMS only).")
    mediaUrls: list[str] | None = Field(
        default=None, description="Public media URLs; presence makes this an MMS."
    )


class MessagingBrandCreateRequest(_Base):
    messagingBrandId: Annotated[str, Field(pattern=r"^B[A-Za-z0-9]+$")]
    messagingBrandName: str
    messagingBrandDescription: str | None = None


class MessagingCampaignCreateRequest(_Base):
    messagingBrandId: str
    externalCampaignId: str
    campaignDescription: str
    campaignClassName: str | None = None
    campaignStartDate: str | None = None


# ----------------------------------------------------------------- Support ---


class TicketCreateRequest(_Base):
    subject: str
    message: str
    email: str | None = Field(default=None, description="Admin only: create on behalf of email.")


class TicketUpdateRequest(_Base):
    status: Literal["active", "pending", "closed", "spam"]


class TicketReplyRequest(_Base):
    message: str


# -------------------------------------------------------------- iNumbering ---


class OrderNumberSpec(_Base):
    number: PhoneNumber
    route: int | None = None


class OrderCreateRequest(_Base):
    numbers: list[PhoneNumber | OrderNumberSpec] = Field(
        description="Up to 100 numbers; each may be a string TN or {number, route?}.",
        max_length=100,
        min_length=1,
    )


class PortFeatureLidb(_Base):
    name: str


class PortFeatureSms(_Base):
    campaignId: str | None = None


class PortFeatureRouting(_Base):
    gatewayId: int


class PortFeature(_Base):
    number: PhoneNumber
    routing: PortFeatureRouting | None = None
    lidb: PortFeatureLidb | None = None
    sms: PortFeatureSms | None = None


class PortSubmitRequest(_Base):
    lcAccountNumber: str
    streetNumber: str
    street: str
    streetSuffix: Literal["", "N", "NE", "E", "SE", "S", "SW", "W", "NW"] | None = None
    building: str | None = None
    city: str
    state: str
    features: list[PortFeature] | None = None


__all__ = [
    "AccountAddRequest",
    "AccountPutRequest",
    "AccountRecoverRequest",
    "AccountSignupRequest",
    "AclModifyRequest",
    "ApiKeyRequest",
    "AuthPutRequest",
    "AuthType",
    "CidrEntry",
    "E911AddressRequest",
    "E911CreateRequest",
    "E911ProvisionByIdRequest",
    "GatewayAddRequest",
    "GatewayUpdateRequest",
    "MessageSendRequest",
    "MessagingBrandCreateRequest",
    "MessagingCampaignCreateRequest",
    "NumberAddRequest",
    "NumberCampaignAssignRequest",
    "NumberCnamRequest",
    "NumberFaxRequest",
    "NumberForwardRequest",
    "NumberLibdRequest",
    "NumberMessagingPatchRequest",
    "NumberMoveRequest",
    "NumberRouteRequest",
    "NumberSmsRequest",
    "NumberTranslationRequest",
    "OrderCreateRequest",
    "OrderNumberSpec",
    "PhoneNumber",
    "PortFeature",
    "PortFeatureLidb",
    "PortFeatureRouting",
    "PortFeatureSms",
    "PortOutPinUpdateRequest",
    "PortSubmitRequest",
    "TicketCreateRequest",
    "TicketReplyRequest",
    "TicketUpdateRequest",
]
