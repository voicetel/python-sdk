"""Fax-resource models — send faxes and read their history and documents."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import PhoneNumber, _Base

FaxJobStatus = Literal["queued", "sending", "retry_pending", "sent", "failed"]
FaxHistoryStatusFilter = Literal[
    "all", "active", "queued", "sending", "retry_pending", "sent", "failed"
]


class FaxNumberEntry(_Base):
    """One fax-capable number on the account."""

    number: PhoneNumber = Field(description="The fax number.")
    destinationId: int = Field(
        description="Per-number fax destination row id, or 0 when it delivers to the account email."
    )
    email: str = Field(description="Email address faxes to this number deliver to.")


class FaxNumbersData(_Base):
    """Data payload from GET /v2.2/numbers/fax."""

    numbers: list[FaxNumberEntry] = Field(description="Fax-capable numbers, ascending.")


class FaxDocumentMeta(_Base):
    """Metadata of one document attached to a fax."""

    name: str = Field(description="File name.")
    size: int = Field(description="Document size in bytes.")
    contentType: str = Field(description="Media type.")


class FaxSendData(_Base):
    """Data payload from POST /v2.2/faxes (202-style acceptance: 201, status queued)."""

    id: str = Field(description="Identifier of the accepted fax job.")
    fromNumber: PhoneNumber = Field(description="The number the fax is sent from.")
    toNumber: PhoneNumber = Field(description="Destination the fax was accepted for.")
    status: Literal["queued"] = Field(description="Job state at acceptance: queued.")
    documents: list[FaxDocumentMeta] = Field(description="The accepted documents.")


class FaxJob(_Base):
    """One fax job: routing, lifecycle timestamps and documents.

    Poll GET /v2.2/faxes/{id} until ``status`` is ``sent`` or ``failed``;
    ``documentAvailable`` tells whether ``document()`` can serve the PDF.
    """

    id: str = Field(description="Fax job identifier.")
    fromNumber: PhoneNumber = Field(description="The number the fax was sent from.")
    toNumber: PhoneNumber = Field(description="The destination.")
    clientToken: str | None = Field(
        default=None, description="The Idempotency-Key the fax was submitted with, or null."
    )
    status: FaxJobStatus = Field(
        description="queued, sending, retry_pending, sent or failed."
    )
    submittedAt: str | None = Field(
        default=None, description="Acceptance time, ISO-8601 UTC."
    )
    startedAt: str | None = Field(
        default=None, description="When delivery was first attempted, ISO-8601 UTC, or null."
    )
    completedAt: str | None = Field(
        default=None, description="When the job reached sent or failed, ISO-8601 UTC, or null."
    )
    attempts: int | None = Field(
        default=None, description="Delivery attempts so far, or null while queued."
    )
    failureReason: str | None = Field(
        default=None, description="Why the fax failed, on failed jobs; null otherwise."
    )
    documents: list[FaxDocumentMeta] = Field(default_factory=list, description="The submitted documents.")
    documentAvailable: bool = Field(
        description="Whether the document endpoint can serve the PDF."
    )
    documentName: str = Field(description="File name the document downloads as.")
    documentSize: int | None = Field(
        default=None, description="Total document size in bytes, or null when there are none."
    )


class FaxHistoryData(_Base):
    """Data payload from GET /v2.2/faxes — one page of history, newest first."""

    number: PhoneNumber = Field(description="The number the history belongs to.")
    fromTs: int = Field(description="Newer edge of the returned range, unix seconds.")
    toTs: int = Field(description="Older edge of the returned range, unix seconds.")
    faxes: list[FaxJob] = Field(description="Fax jobs, newest first.")
    nextCursor: str | None = Field(
        default=None, description="Cursor for the next page, or null when the page is the last."
    )
