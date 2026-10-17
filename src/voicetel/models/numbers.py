"""Numbers-resource models — every operation on a TN owned by the account."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from ._base import PhoneNumber, _Base

# ----------------------------------------------------------------- requests ---


class NumberAddRequest(_Base):
    """POST /v2.2/numbers."""

    number: PhoneNumber = Field(description="10-digit TN to attach to the account.")
    route: int | None = Field(
        default=None,
        description="Global route type: 1 USER, 2 T30, 3 VOICE_BRIDGE, 4 DID (default), "
        "5 T38, 6 VOICEML, 8 SDN, 9 MOBILE. Used when adding a number.",
    )


class NumberRouteRequest(_Base):
    """PUT /v2.2/numbers/{number}/route."""

    route: int = Field(
        description="Global route type: 1 USER, 2 T30, 3 VOICE_BRIDGE, 4 DID (default), "
        "5 T38, 6 VOICEML, 8 SDN, 9 MOBILE. Set with PUT /v2.2/numbers/{number}/route.",
    )


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

    destination: PhoneNumber = Field(description="10-digit destination number.")


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
    """PATCH /v2.2/numbers/{number}/messaging — update inbound and/or outbound routing.

    At least one of ``routeIn`` / ``routeOut`` must be present. ``routeIn`` must be a
    numbers_sms row id owned by the authenticated account, or 0 to detach. ``routeOut``
    must be 0 (outbound off) or the route the number is enabled on; to move a number to
    another campaign or messaging path use PUT /v2.2/numbers/{number}/messaging-campaign.
    """

    routeIn: int | None = Field(
        default=None,
        description="numbers_sms row id for inbound. 0 to detach.",
    )
    routeOut: int | None = Field(
        default=None,
        description="Outbound carrier id.",
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
    route: int = Field(
        description="Global route type: 1 USER, 2 T30, 3 VOICE_BRIDGE, 4 DID (default), "
        "5 T38, 6 VOICEML, 8 SDN, 9 MOBILE. Per-number route in the list.",
    )
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
MessagingStateNetwork = Literal["A", "B", "C"]

MessagingEnablementJobState = Literal[
    "queued", "hosting", "assigning", "routing", "done", "failed"
]


class MessagingEnablementJob(_Base):
    """State of an asynchronous (path C) enablement.

    Attached to a campaign assignment (status ``pending``) or surfaced by
    GET /v2.2/numbers/{number}/messaging while provisioning is in flight.
    """

    campaignId: str = Field(description="TCR campaign id being enabled.")
    state: MessagingEnablementJobState = Field(
        description=(
            "queued -> hosting -> assigning -> routing -> done, or failed (see message). "
            "The number keeps its previous routing until done."
        ),
    )
    message: str = Field(description="Latest progress note, or the reason for failure.")
    createdAt: str = Field(description="ISO 8601 timestamp the job was created.")
    updatedAt: str = Field(description="ISO 8601 timestamp of the latest progress update.")


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
    network: MessagingStateNetwork | None = Field(
        default=None,
        description="Messaging path the number is currently on. null when carrier is 0 "
        "or any non-messaging carrier.",
    )
    campaign: CampaignBinding | None = Field(
        default=None,
        description="Bound campaign with CSP-side status. null when no binding exists.",
    )
    pending: MessagingEnablementJob | None = Field(
        default=None,
        description="Async path-C enablement in progress for this number; null when none.",
    )


# ------------------------------------------------------- per-op data shapes ---


class NumberAddData(_Base):
    """Data payload from POST /v2.2/numbers."""

    number: PhoneNumber
    route: int = Field(
        description="Global route type: 1 USER, 2 T30, 3 VOICE_BRIDGE, 4 DID (default), "
        "5 T38, 6 VOICEML, 8 SDN, 9 MOBILE. Returned after adding a number.",
    )


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
    route: int = Field(
        description="Global route type: 1 USER, 2 T30, 3 VOICE_BRIDGE, 4 DID (default), "
        "5 T38, 6 VOICEML, 8 SDN, 9 MOBILE. Route on the destination account after the move.",
    )


class NumberRouteData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/route."""

    number: PhoneNumber
    route: int = Field(
        description="Global route type: 1 USER, 2 T30, 3 VOICE_BRIDGE, 4 DID (default), "
        "5 T38, 6 VOICEML, 8 SDN, 9 MOBILE. Echo of the applied route.",
    )


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


PreviousNetwork = Literal["A", "B"]

CampaignAssignStatus = Literal["enabled", "already", "pending"]
CampaignAssignNetwork = Literal["B", "C"]


class NumberMessagingCampaignAssignData(_Base):
    """Data payload from PUT /v2.2/numbers/{number}/messaging-campaign.

    Result of binding a single number to a 10DLC campaign: ``status`` "enabled" (path B,
    bound synchronously — HTTP 200), "already" (the number was already bound to this
    campaign — idempotent no-op), or "pending" (path C, provisioned asynchronously —
    HTTP 202; poll GET /v2.2/numbers/{number}/messaging until the job's state is
    ``done`` or ``failed``).
    """

    number: PhoneNumber
    campaignId: str = Field(description="7-character TCR campaign id.")
    status: CampaignAssignStatus = Field(
        description=(
            'enabled = bound now (path B); already = the number was already bound to this '
            'campaign (records reconciled, no new order); pending = accepted and being '
            'provisioned (path C) -- poll GET /v2.2/numbers/{number}/messaging (pending) '
            "until state is done or failed."
        ),
    )
    network: CampaignAssignNetwork | None = Field(
        description='Messaging path the campaign resolves to (from the CSP sharing record). '
        'Path B is assigned synchronously; path C is provisioned asynchronously '
        '(status "pending").',
    )
    upstreamCnpId: str | None = Field(
        description="CNP ID from the CSP sharing record: CAMP003 = path B, BANDW = path C. "
        "(Campaigns on path A, CAMP004, are being migrated and take no new numbers.)",
    )
    carrier: int = Field(
        description="Outbound carrier id the number routes through once enabled "
        "(19 = path B, 1 = path C). For a pending path-C enablement the number keeps its "
        "current routing until provisioning completes.",
    )
    alreadyAssigned: bool = Field(
        description="True when the number was already bound to this campaign on the target "
        "messaging path; records are reconciled and no new network order is placed.",
    )
    orderId: str | int | None = Field(
        default=None,
        description="Network order id created for a path-B assignment. Null for path C "
        "(see job), idempotent no-ops, and assignments confirmed without a new order.",
    )
    previousNetwork: PreviousNetwork | None = Field(
        description="Messaging path the number was bound to before this call — null if "
        "there was no prior binding, 'A' or 'B' if a conflict was detected.",
    )
    previousNetworkCleared: bool = Field(
        description="True if a conflicting binding on the other path was successfully "
        "disabled to allow this assignment.",
    )
    warning: str | None = Field(
        default=None,
        description="Non-fatal condition detected during the assignment (for example a "
        "stale registration on the other messaging path whose removal has been requested).",
    )
    message: str | None = Field(
        default=None,
        description="Human-readable note for a pending enablement.",
    )
    job: MessagingEnablementJob | None = Field(
        default=None,
        description="Async enablement job when status is 'pending' (path C); null otherwise.",
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
    """Data payload from PATCH /v2.2/numbers/{number}/port-out-pin.

    The call is idempotent: a PIN is locked for 30 days once set, so a number that
    already has one returns it unchanged with ``changed=false``; both cases return
    HTTP 200.
    """

    number: PhoneNumber = Field(description="Ten-digit telephone number whose PIN is reported.")
    portOutPin: Annotated[str, Field(pattern=r"^[0-9]{4}$")] = Field(
        description="The port-out PIN now on file for this number (the value just set, or "
        "the existing value if the number was already locked).",
    )
    changed: bool = Field(
        description="True if this request set the PIN; false if the number already had one, "
        "which is locked for 30 days once set and is returned unchanged.",
    )
