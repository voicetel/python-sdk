"""Numbers-resource models — every operation on a TN owned by the account."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from ._base import PhoneNumber, _Base

# ----------------------------------------------------------------- requests ---


class NumberAddRequest(_Base):
    """POST /v2.2/numbers."""

    number: PhoneNumber = Field(description="10-digit TN to attach to the account.")
    route: int | None = Field(default=None, description="Gateway route ID; defaults to 4 (DID).")


class NumberRouteRequest(_Base):
    """PUT /v2.2/numbers/{number}/route."""

    route: int


class NumberCnamRequest(_Base):
    """PUT /v2.2/numbers/{number}/cnam — inbound CNAM toggle."""

    enabled: bool


class NumberLidbRequest(_Base):
    """PUT /v2.2/numbers/{number}/lidb — outbound caller name (LIDB)."""

    cnam: str = Field(description="Outbound caller name. Max 15 alphanumeric chars.")
    customerOrderReference: str | None = None


class NumberFaxRequest(_Base):
    """PUT /v2.2/numbers/{number}/fax."""

    email: str


class NumberForwardRequest(_Base):
    """PUT /v2.2/numbers/{number}/forward."""

    destination: int = Field(description="10-digit destination number.")


class NumberTranslationRequest(_Base):
    """PUT /v2.2/numbers/{number}/translation."""

    translation: str = Field(description="DNIS translation. Digits and # only.")


SmsRouteType = Literal["email", "webhook", "sip"]


class NumberSmsRequest(_Base):
    """PUT /v2.2/numbers/{number}/sms."""

    type: SmsRouteType = Field(
        description="email=forward to email, webhook=HTTP POST, sip=direct IP delivery.",
    )
    resource: str = Field(
        description="Destination — email, webhook URL, or IP, depending on ``type``.",
    )


class NumberMessagingPatchRequest(_Base):
    """PATCH /v2.2/numbers/{number}/messaging — update inbound and/or outbound routing."""

    routeIn: int | None = Field(
        default=None,
        description="numbers_sms row id for inbound. 0 to detach.",
    )
    routeOut: int | None = Field(
        default=None,
        description="Outbound carrier id (numbers.carrier value).",
    )


class NumberCampaignAssignRequest(_Base):
    """PUT /v2.2/numbers/{number}/messaging-campaign."""

    campaignId: Annotated[str, Field(pattern=r"^[A-Z0-9]+$")] = Field(
        description="7-character TCR campaign id.",
    )


class NumberMoveRequest(_Base):
    """PATCH /v2.2/numbers/{number} — move to another account."""

    accountId: int = Field(description="Destination account id (numeric username).")
    route: int


class PortOutPinUpdateRequest(_Base):
    """PATCH /v2.2/numbers/{number}/port-out-pin."""

    pin: Annotated[str, Field(pattern=r"^[0-9]{4}$")] = Field(
        description="Four-digit numeric PIN.",
    )


# ------------------------------------------------------- entities & responses ---


class NumberDetail(_Base):
    """Per-number routing / feature state. Returned by GET /v2.2/numbers and /v2.2/numbers/{number}."""

    number: PhoneNumber
    translated: PhoneNumber = Field(
        description="Destination after translation rewrite — usually equals ``number``.",
    )
    route: int = Field(description="Gateway id the number is currently routed to.")
    gateway: str | None = Field(
        default=None,
        description="Gateway address (IP[:port]) or system route name.",
    )
    cnam: bool = Field(description="Inbound CNAM lookup enabled.")
    forward: bool
    forwardTo: str | None = Field(
        default=None,
        description="Forwarding destination — 10-digit TN, or null when forwarding is disabled.",
    )
    carrier: int = Field(description="Outbound messaging carrier identifier.")
    smsEnabled: bool
    faxEnabled: bool


MessagingNetwork = Literal["A", "B"]


class CampaignBinding(_Base):
    """The campaign bound to a number, with its CSP-side status."""

    id: str = Field(description="TCR campaign id.")
    network: MessagingNetwork = Field(description="Messaging path (A or B).")
    status: str = Field(description="CSP campaign status: ACTIVE, EXPIRED, SUSPENDED, etc.")
    upstreamCnpId: str = Field(description="CNP id from the CSP sharing record.")


class NumberMessagingState(_Base):
    """Current messaging routing state for one number."""

    number: PhoneNumber
    onAccount: bool | None = Field(
        default=None,
        description="Present and false when the number is not on the authenticated account.",
    )
    enabled: bool
    carrier: int = Field(description="Internal carrier identifier on the numbers row.")
    routeIn: int = Field(description="numbers_sms row id for inbound; 0 = none.")
    resource: str = Field(description="URL or endpoint that receives inbound messages.")
    network: MessagingNetwork | None = Field(
        default=None,
        description="Messaging path. null when carrier is 0 or non-messaging.",
    )
    campaign: CampaignBinding | None = Field(
        default=None,
        description="Bound campaign with CSP-side status. null when no binding exists.",
    )


# ------------------------------------------------------- per-op data shapes ---


class NumberAddData(_Base):
    """Data payload from POST /v2.2/numbers."""

    number: PhoneNumber
    route: int = Field(description="Gateway id the number is currently routed to.")


class NumberCnamData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/cnam."""

    number: PhoneNumber
    cnam: bool = Field(description="Updated CNAM-enabled state.")


class NumberFaxData(_Base):
    """Data payload from GET/PUT /v2.2/numbers/{number}/fax."""

    number: PhoneNumber
    email: str


class NumberForwardData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/forward."""

    number: PhoneNumber
    forwardTo: str | None = Field(
        description="Forwarding destination — 10-digit TN — or null when disabled.",
    )


class NumberLidbData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/lidb."""

    number: PhoneNumber
    cnam: str = Field(description="Sanitised caller name (max 15 alphanumeric).")
    customerOrderReference: str = Field(
        description="Echoed if supplied; auto-generated as '<username>-<unix-ts>' otherwise.",
    )
    carrierStatus: str = Field(
        description="Status returned by the LIDB network. 'Success' = accepted.",
    )


NumberMessagingPatchField = Literal["routeIn", "routeOut"]


class NumberMessagingPatchData(_Base):
    """Data payload from PATCH /v2.2/numbers/{number}/messaging."""

    number: PhoneNumber
    updated: list[NumberMessagingPatchField] = Field(
        description="Subset of {routeIn, routeOut} the request changed.",
    )


class NumberMoveData(_Base):
    """Data payload from PATCH /v2.2/numbers/{number}."""

    number: PhoneNumber
    accountId: int = Field(description="Destination account the number was moved to.")
    route: int = Field(description="gateway_id on the destination account.")


class NumberRouteData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/route."""

    number: PhoneNumber
    route: int


class NumberSmsData(_Base):
    """Data payload from GET/PUT /v2.2/numbers/{number}/sms."""

    number: PhoneNumber
    type: Literal["email", "webhook", "sip", "unknown"]
    resource: str


class NumberTranslationData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/translation."""

    number: PhoneNumber
    translation: PhoneNumber = Field(
        description="Destination digits used when translation is applied.",
    )


PreviousNetwork = Literal["A", "B", "unknown"]


class NumberMessagingCampaignAssignData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/messaging-campaign."""

    number: PhoneNumber
    campaignId: str = Field(description="7-character TCR campaign id.")
    carrier: int = Field(description="Outbound carrier id (17=path A, 19=path B).")
    network: MessagingNetwork | None = Field(
        description="Messaging path the campaign resolves to.",
    )
    upstreamCnpId: str | None = Field(description="CNP id from the CSP sharing record.")
    previousNetwork: PreviousNetwork | None = Field(
        description="Path the number was on before this assignment, if any.",
    )
    previousNetworkCleared: bool = Field(
        description="True if a prior conflicting binding was disabled to allow this one.",
    )


class NumberMessagingCampaignUnassignData(_Base):
    """Data payload from DELETE /v2.2/numbers/{number}/messaging-campaign."""

    number: PhoneNumber
    campaignId: str = Field(description="Campaign id the number was removed from.")
    network: MessagingNetwork | None = Field(description="Path before unassignment.")
    upstreamCnpId: str | None = Field(description="CNP id from the CSP sharing record.")
    unassigned: bool = Field(description="Always true on a 200 response.")


class CampaignUnassignFailure(_Base):
    """One row in the failure list returned by bulk unassign."""

    number: PhoneNumber
    reason: str


class NumbersMessagingCampaignUnassignData(_Base):
    """Data payload from DELETE /v2.2/numbers/messaging-campaign (bulk)."""

    campaignId: str
    network: MessagingNetwork | None = None
    upstreamCnpId: str | None = None
    unassignedNumbers: list[str] = Field(
        description="Numbers whose binding was successfully removed.",
    )
    failed: list[CampaignUnassignFailure] = Field(
        default_factory=list,
        description="Numbers whose unassignment failed, with reasons.",
    )


class NumbersListData(_Base):
    """Data payload from GET /v2.2/numbers."""

    numbers: list[NumberDetail]


class NumbersMessagingListData(_Base):
    """Data payload from GET /v2.2/numbers/messaging."""

    numbers: list[NumberMessagingState]


class PortOutPinUpdateData(_Base):
    """Data payload from PATCH /v2.2/numbers/{number}/port-out-pin."""

    number: PhoneNumber
    portOutPin: Annotated[str, Field(pattern=r"^[0-9]{4}$")]
