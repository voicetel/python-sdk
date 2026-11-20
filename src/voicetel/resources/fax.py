"""Fax resource — send faxes and read their history and documents."""

from __future__ import annotations

import uuid as _uuid
from dataclasses import dataclass
from typing import Any, cast

from ..models import (
    FaxHistoryData,
    FaxHistoryStatusFilter,
    FaxJob,
    FaxNumbersData,
    FaxSendData,
)
from ._base import AsyncResource, Resource, quote_path, unwrap


@dataclass(frozen=True)
class FaxDocument:
    """One document to send: file name, raw bytes, and media type.

    ``content_type`` is validated by content (magic bytes) server-side; PDF,
    DOC and DOCX are accepted. At most 8 MiB per document and in total.
    """

    name: str
    content: bytes
    content_type: str = "application/pdf"

    @classmethod
    def pdf(cls, name: str, content: bytes) -> FaxDocument:
        return cls(name=name, content=content, content_type="application/pdf")


class FaxResource(Resource):
    """Send faxes from the account's fax numbers and read their history."""

    def list_numbers(self) -> FaxNumbersData:
        """GET /v2.2/numbers/fax — every fax-capable number on the account."""
        return FaxNumbersData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/numbers/fax"))
        )

    def send(
        self,
        *,
        from_number: str,
        to_number: str,
        documents: list[FaxDocument],
        idempotency_key: str | None = None,
    ) -> FaxSendData:
        """POST /v2.2/faxes — submit a fax for delivery (multipart, 201).

        ``idempotency_key`` (a UUID) is generated when omitted; pass your own to
        make retries safe across process restarts — the same documents with the
        same key return the original job instead of sending twice.
        """
        return FaxSendData.model_validate(
            unwrap(
                self._t.request(
                    "POST",
                    "/v2.2/faxes",
                    data={"fromNumber": from_number, "toNumber": to_number},
                    files=[
                        ("documents", (d.name, d.content, d.content_type))
                        for d in documents
                    ],
                    idempotency_key=idempotency_key or str(_uuid.uuid4()),
                )
            )
        )

    def history(
        self,
        *,
        number: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        status: FaxHistoryStatusFilter | None = None,
    ) -> FaxHistoryData:
        """GET /v2.2/faxes — one page of history for a fax number, newest first.

        ``from_ts``/``to_ts`` are unix seconds (``from_ts`` is the newer edge);
        the default range is the last 24 hours.
        """
        params: dict[str, Any] = {"number": number}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        return FaxHistoryData.model_validate(
            unwrap(self._t.request("GET", "/v2.2/faxes", params=params))
        )

    def get(self, fax_id: str) -> FaxJob:
        """GET /v2.2/faxes/{id} — one fax job."""
        return FaxJob.model_validate(
            unwrap(self._t.request("GET", f"/v2.2/faxes/{quote_path(fax_id)}"))
        )

    def document(self, fax_id: str) -> bytes:
        """GET /v2.2/faxes/{id}/document — the fax PDF as raw bytes."""
        return cast(
            bytes,
            self._t.request(
                "GET", f"/v2.2/faxes/{quote_path(fax_id)}/document", raw=True
            ),
        )


class FaxAsyncResource(AsyncResource):
    async def list_numbers(self) -> FaxNumbersData:
        return FaxNumbersData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/numbers/fax"))
        )

    async def send(
        self,
        *,
        from_number: str,
        to_number: str,
        documents: list[FaxDocument],
        idempotency_key: str | None = None,
    ) -> FaxSendData:
        return FaxSendData.model_validate(
            unwrap(
                await self._t.request(
                    "POST",
                    "/v2.2/faxes",
                    data={"fromNumber": from_number, "toNumber": to_number},
                    files=[
                        ("documents", (d.name, d.content, d.content_type))
                        for d in documents
                    ],
                    idempotency_key=idempotency_key or str(_uuid.uuid4()),
                )
            )
        )

    async def history(
        self,
        *,
        number: str,
        from_ts: int | None = None,
        to_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        status: FaxHistoryStatusFilter | None = None,
    ) -> FaxHistoryData:
        params: dict[str, Any] = {"number": number}
        if from_ts is not None:
            params["from"] = from_ts
        if to_ts is not None:
            params["to"] = to_ts
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        return FaxHistoryData.model_validate(
            unwrap(await self._t.request("GET", "/v2.2/faxes", params=params))
        )

    async def get(self, fax_id: str) -> FaxJob:
        return FaxJob.model_validate(
            unwrap(await self._t.request("GET", f"/v2.2/faxes/{quote_path(fax_id)}"))
        )

    async def document(self, fax_id: str) -> bytes:
        return cast(
            bytes,
            await self._t.request(
                "GET", f"/v2.2/faxes/{quote_path(fax_id)}/document", raw=True
            ),
        )
