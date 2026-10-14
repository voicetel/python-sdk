"""Messaging-resource models — SMS/MMS, 10DLC brands and campaigns."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from ._base import PhoneNumber, _Base

# ----------------------------------------------------------------- requests ---


class MessageSendRequest(_Base):
    """POST /v2.2/messages — send an SMS or MMS.

    ``mediaUrls`` switches the message type to MMS (and unlocks ``subject``).
    Note the wire field names ``fromNumber`` / ``toNumber`` — these were renamed (from the older
    ``from`` / ``to``) to avoid the Python/JavaScript ``from`` reserved-word collision.
    """

    fromNumber: PhoneNumber = Field(description="Source 10-digit TN on the authenticated account.")
    toNumber: PhoneNumber = Field(description="Destination 10-digit TN.")
    text: str = Field(description="Message body (UTF-8).")
    subject: str | None = Field(default=None, description="MMS subject line (MMS only).")
    mediaUrls: list[str] | None = Field(
        default=None,
        description="Public media URLs; presence makes this an MMS.",
    )


class MessagingBrandCreateRequest(_Base):
    """POST /v2.2/messaging/brands."""

    messagingBrandId: Annotated[str, Field(pattern=r"^B[A-Za-z0-9]+$")] = Field(
        description="Brand id issued by the campaign registry. Starts with `B`.",
    )
    messagingBrandName: str = Field(description="Brand display name.")
    messagingBrandDescription: str | None = Field(
        default=None,
        description="Free-form description of the brand.",
    )


class MessagingCampaignCreateRequest(_Base):
    """POST /v2.2/messaging/campaigns.

    ``campaignClassName`` (from the campaign registry) and ``campaignStartDate``
    (today) are auto-populated if omitted.
    """

    messagingBrandId: str
    externalCampaignId: str
    campaignDescription: str
    campaignClassName: str | None = None
    campaignStartDate: str | None = Field(default=None, description="ISO 8601 timestamp.")


# ----------------------------------------------------------- data shapes ---


MessageType = Literal["sms", "mms"]
MessageHistoryType = Literal["sms", "mms", "dlr"]
MessageDirection = Literal["in", "out"]


class MessageRecordValue(_Base):
    """Per-record fields inside :class:`MessageRecord`. Shape varies by ``type``.

    For ``sms``/``mms``: ``sourceNumber``, ``destinationNumber``, ``direction``, ``rate``,
    ``message`` populated; ``number`` is set to a sentinel integer (the spec types it as
    integer even though SMS/MMS records carry actual TNs as strings via the other fields).

    For ``dlr``: ``sourceNumber`` and ``destinationNumber`` populated.
    """

    sourceNumber: str | None = None
    destinationNumber: str | None = None
    direction: MessageDirection | None = Field(
        default=None,
        description="SMS/MMS only.",
    )
    rate: str | None = Field(
        default=None,
        description="Billed rate per message (string for precision; SMS/MMS only).",
    )
    number: int | None = Field(default=None, description="Far-end number (SMS/MMS only).")
    message: str | None = Field(default=None, description="Message body (SMS/MMS only).")


class MessageRecord(_Base):
    """One row in :class:`MessageHistoryData.messages`."""

    id: str = Field(description="Record identifier.")
    key: list[str | int | None] = Field(
        description=(
            "Composite range key. For sms/mms: [destinationNumber, timestamp]. "
            "For dlr: [accountId, fromNumberWithCountryCode, timestamp]."
        ),
    )
    value: MessageRecordValue


class MessageHistoryData(_Base):
    """Data payload from GET /v2.2/messages."""

    number: PhoneNumber = Field(description="The TN whose messages are returned.")
    type: MessageHistoryType = Field(description="Echo of the requested message type.")
    fromTs: int = Field(description="Unix timestamp range start.")
    toTs: int = Field(description="Unix timestamp range end (older than fromTs).")
    messages: list[MessageRecord] = Field(
        description="MDRs (or DLRs when type=dlr) for the range, newest first.",
    )


class MessageSendData(_Base):
    """Data payload from POST /v2.2/messages."""

    id: str = Field(description="Provider transaction id.")
    type: MessageType
    fromNumber: PhoneNumber
    toNumber: PhoneNumber
    parts: int = Field(description="Number of SMS segments billed; 1 for MMS.")
    subject: str | None = Field(default=None, description="Echo of submitted subject (MMS only).")
    mediaUrls: list[str] | None = None


class BrandRegistrationResult(_Base):
    """Status payload for brand registration."""

    statusCode: str = Field(description="HTTP status code as string; '200' on success.")
    status: str = Field(description="Status text, e.g. 'Success'.")


class MessagingBrandCreateData(_Base):
    """Data payload from POST /v2.2/messaging/brands."""

    result: BrandRegistrationResult


class CampaignRegistrationResult(_Base):
    """Status payload for campaign registration."""

    statusCode: str
    status: str


class MessagingCampaignCreateData(_Base):
    """Data payload from POST /v2.2/messaging/campaigns."""

    result: CampaignRegistrationResult


class CampaignDcaCarrier(_Base):
    """One carrier's latest DCA decision in :class:`CampaignDca`."""

    carrier: str = Field(description="Carrier name, e.g. 'T-Mobile'.")
    status: str = Field(
        description="Carrier decision: ACTIVE, REJECTED, SUSPENDED, UNSUSPENDED or TERMINATED.",
    )
    detail: str = Field(description="The reviewer's note, as given.")
    updatedAt: str = Field(description="ISO 8601 timestamp of the decision.")


class CampaignDca(_Base):
    """Carrier (DCA) review progress for a campaign.

    ``null`` for ``CAMPAIGN_INVALID_ID`` statuses.
    """

    electionComplete: bool = Field(
        description="True once every carrier has a DCA assigned to review the campaign.",
    )
    electedCarriers: list[str] | None = Field(
        default=None,
        description="Carriers with a DCA assigned so far (null when unavailable).",
    )
    carriers: list[CampaignDcaCarrier] = Field(
        description="Each carrier DCA decision received, latest per carrier.",
    )


class CampaignStatusItem(_Base):
    """A single campaign and its current numbers."""

    id: str = Field(description="TCR campaign id.")
    status: str = Field(
        description=(
            "Campaign status: CAMPAIGN_DCA_COMPLETE (ready: carrier review finished, "
            "numbers assigned), CAMPAIGN_DCA_COMPLETE_NO_NUMBERS_ASSIGNED, "
            "CAMPAIGN_PENDING_DCA (active at the campaign registry, but carrier (DCA) "
            "review is not finished yet; numbers cannot be enabled until it is), "
            "CAMPAIGN_DCA_REJECTED (a carrier's DCA rejected or suspended the campaign; "
            "see dca.carriers), CAMPAIGN_<registry status>, or CAMPAIGN_INVALID_ID."
        ),
    )
    numbers: list[str] = Field(description="Numbers currently bound to the campaign.")
    dca: CampaignDca | None = Field(
        default=None,
        description="Carrier (DCA) review progress. null for CAMPAIGN_INVALID_ID.",
    )


class MessagingCampaignStatusData(_Base):
    """Data payload from GET /v2.2/messaging/campaigns."""

    campaigns: list[CampaignStatusItem]
