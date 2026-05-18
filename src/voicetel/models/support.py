"""Support-resource models — tickets, replies, and the underlying conversation/thread shapes.

Note on the ``supportConversation.number`` field: the OpenAPI spec types it as ``integer``
(it's the human-readable ticket number, e.g. #1015, not a phone number). The SDK exposes
it as :attr:`SupportConversation.ticket_number` via a Pydantic alias so callers don't confuse
it with phone-number TNs.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ._base import _Base

# ----------------------------------------------------------------- requests ---


class TicketCreateRequest(_Base):
    """POST /v2.2/support/tickets."""

    subject: str
    message: str
    email: str | None = Field(
        default=None,
        description="Admin only: create the ticket on behalf of this customer email.",
    )


TicketStatus = Literal["active", "pending", "closed", "spam"]


class TicketUpdateRequest(_Base):
    """PUT /v2.2/support/tickets/{id}."""

    status: TicketStatus


class TicketReplyRequest(_Base):
    """POST /v2.2/support/tickets/{id}/replies."""

    message: str


# --------------------------------------------------------- shared subtypes ---


class TicketSource(_Base):
    """Provenance of a ticket or thread."""

    via: str | None = None
    type: str | None = None


class TicketAction(_Base):
    """Action descriptor on a thread."""

    text: str | None = None
    type: str | None = None


class TicketActor(_Base):
    """``createdBy`` / ``assignee`` / ``assignedTo`` / ``closedByUser`` shape."""

    id: int | None = None
    type: str | None = Field(default=None, description="e.g. 'customer' or 'user'.")
    email: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    photoUrl: str | None = None


class CustomFieldValue(_Base):
    """One custom-field row on a conversation."""

    id: int | None = None
    value: str | None = None
    text: str | None = None


class CustomerContactEntry(_Base):
    """A single ``{id, value, type}`` entry under ``embedded.{emails|phones|socialProfiles}``."""

    id: int | None = None
    value: str | None = None
    type: str | None = None


class CustomerWebsiteEntry(_Base):
    """A single ``{id, value}`` entry under ``embedded.websites``."""

    id: int | None = None
    value: str | None = None


class CustomerAddress(_Base):
    """``embedded.address`` shape on a support customer."""

    street: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, description="Two-letter US state code.")
    country: str | None = Field(default=None, description="ISO 3166-1 alpha-2 country code.")
    zip: str | None = None


class CustomerEmbedded(_Base):
    """``embedded`` shape on :class:`SupportCustomer`."""

    address: CustomerAddress | None = None
    emails: list[CustomerContactEntry] | None = None
    phones: list[CustomerContactEntry] | None = None
    socialProfiles: list[CustomerContactEntry] | None = None
    websites: list[CustomerWebsiteEntry] | None = None


# -------------------------------------------------------------- attachments ---


class SupportAttachment(_Base):
    """One file attached to a support thread."""

    id: int | None = None
    mimeType: str | None = None
    fileName: str | None = None
    fileUrl: str | None = None
    size: int | None = Field(default=None, description="File size in bytes.")


class ThreadEmbedded(_Base):
    """``embedded`` shape on :class:`SupportThread`."""

    attachments: list[SupportAttachment] | None = None


class ConversationEmbedded(_Base):
    """``embedded`` shape on :class:`SupportConversation` — typically wraps threads."""

    threads: list[SupportThread] | None = None


# ----------------------------------------------------------------- entities ---


class SupportCustomer(_Base):
    """End-user profile attached to a support ticket."""

    id: int | None = None
    firstName: str | None = None
    lastName: str | None = None
    email: str | None = None
    company: str | None = Field(default=None, description="Free-form, max 60 chars.")
    jobTitle: str | None = None
    photoType: str | None = None
    photoUrl: str | None = None
    notes: str | None = None
    type: str | None = Field(default=None, description="Always 'customer'.")
    createdAt: str | None = None
    updatedAt: str | None = None
    embedded: CustomerEmbedded | None = None


class SupportThread(_Base):
    """One thread (message) within a ticket conversation."""

    id: int | None = Field(default=None, description="Thread identifier — unique within ticket.")
    status: TicketStatus
    state: str | None = None
    type: Literal["customer", "message", "note"] | None = Field(
        default=None,
        description="customer = from the user; message = staff reply; note = internal note.",
    )
    body: str | None = None
    rating: int | None = None
    ratingComment: str | None = None
    openedAt: str | None = None
    createdAt: str | None = None
    source: TicketSource | None = None
    action: TicketAction | None = None
    createdBy: TicketActor | None = None
    assignedTo: TicketActor | None = None
    customer: SupportCustomer | None = None
    to: list[str] | None = Field(default=None, description="Recipients of outbound messages.")
    cc: list[str] | None = None
    bcc: list[str] | None = None
    embedded: ThreadEmbedded | None = None


class SupportConversation(_Base):
    """A support ticket. Returned by GET /v2.2/support/tickets/{id} and items of the list endpoint.

    Note ``number`` is the human-readable ticket sequence (#1015), not a phone number. We
    expose it as ``ticket_number`` in Python; the wire field name is ``number``.
    """

    id: int | None = Field(default=None, description="Ticket identifier — use as {id} in subsequent calls.")
    ticket_number: int | None = Field(
        default=None,
        alias="number",
        description="Human-readable ticket sequence shown to the customer (e.g. 1015).",
    )
    status: TicketStatus
    state: str | None = None
    subject: str | None = None
    preview: str | None = None
    type: str | None = Field(default=None, description="e.g. 'email'.")
    mailboxId: int | None = None
    folderId: int | None = None
    threadsCount: int | None = None
    closedBy: int | None = None
    closedAt: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None
    userUpdatedAt: str | None = None
    customerWaitingSince: dict[str, Any] | None = Field(
        default=None,
        description="Free-form 'customer has been waiting' object.",
    )
    source: TicketSource | None = None
    createdBy: TicketActor | None = None
    assignee: TicketActor | None = None
    closedByUser: TicketActor | None = None
    customer: SupportCustomer | None = None
    cc: list[str] | None = None
    bcc: list[str] | None = None
    customFields: list[CustomFieldValue] | None = None
    embedded: ConversationEmbedded | None = None


# Resolve the forward reference in ConversationEmbedded.threads
ConversationEmbedded.model_rebuild()


# ----------------------------------------------------------- data shapes ---


class TicketData(_Base):
    """Data payload from GET /v2.2/support/tickets/{id}."""

    ticket: SupportConversation


class TicketsListData(_Base):
    """Data payload from GET /v2.2/support/tickets."""

    tickets: list[SupportConversation]


class TicketThreadsData(_Base):
    """Data payload from GET /v2.2/support/tickets/{id}/messages."""

    messages: list[SupportThread]


class TicketReplyData(_Base):
    """Data payload from POST /v2.2/support/tickets/{id}/replies."""

    message: Literal["Reply added"] = Field(description="Confirmation message.")


class TicketUpdateData(_Base):
    """Data payload from PUT /v2.2/support/tickets/{id}."""

    id: int | None = None
    status: str = Field(description="Outcome of the update operation, e.g. 'success'.")
