"""Wire-shape tests for the v2.2.21 additions, asserted against the v2.2 spec.

Covers:
- GET /v2.2/numbers/fax (fax-capable numbers)
- POST /v2.2/faxes (multipart send, Idempotency-Key header, 201)
- GET /v2.2/faxes (history query params, cursor page)
- GET /v2.2/faxes/{id} (job shape)
- GET /v2.2/faxes/{id}/document (binary PDF download)
- DELETE /v2.2/acl now takes the {acl: [...]} body (also covered in test_resources)
"""

from __future__ import annotations

import json
import re

import httpx
import pytest
import respx

from voicetel import AsyncClient, Client
from voicetel.models import FaxHistoryData, FaxJob, FaxNumbersData, FaxSendData
from voicetel.resources import FaxDocument

from .test_resources import BASE, env

JOB = {
    "id": "9f8c2b41a",
    "fromNumber": "2015550123",
    "toNumber": "2125550123",
    "clientToken": "123e4567-e89b-12d3-a456-426614174000",
    "status": "sent",
    "submittedAt": "2026-11-20T15:04:05Z",
    "startedAt": "2026-11-20T15:04:41Z",
    "completedAt": "2026-11-20T15:05:19Z",
    "attempts": 1,
    "failureReason": None,
    "documents": [{"name": "contract.pdf", "size": 123456, "contentType": "application/pdf"}],
    "documentAvailable": True,
    "documentName": "contract.pdf",
    "documentSize": 123456,
}


def test_fax_list_numbers(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.get("/v2.2/numbers/fax").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {"numbers": [{"number": "2015550123", "destinationId": 7, "email": "fax@example.com"}]}
            ),
        )
    )
    result = client.fax.list_numbers()
    assert isinstance(result, FaxNumbersData)
    assert result.numbers[0].number == "2015550123"
    assert result.numbers[0].destinationId == 7
    assert route.called


def test_fax_send_multipart(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.post("/v2.2/faxes").mock(
        return_value=httpx.Response(
            201,
            json=env(
                {
                    "id": "9f8c2b41a",
                    "fromNumber": "2015550123",
                    "toNumber": "2125550123",
                    "status": "queued",
                    "documents": [
                        {"name": "contract.pdf", "size": 123456, "contentType": "application/pdf"}
                    ],
                }
            ),
        )
    )
    result = client.fax.send(
        from_number="2015550123",
        to_number="2125550123",
        documents=[FaxDocument.pdf("contract.pdf", b"%PDF-1.4 fake")],
        idempotency_key="123e4567-e89b-12d3-a456-426614174000",
    )
    assert isinstance(result, FaxSendData)
    assert result.status == "queued"
    assert result.documents[0].name == "contract.pdf"

    request = route.calls.last.request
    # multipart with a boundary
    content_type = request.headers["content-type"]
    assert content_type.startswith("multipart/form-data; boundary=")
    body = request.content
    assert b'name="fromNumber"' in body and b"2015550123" in body
    assert b'name="toNumber"' in body and b"2125550123" in body
    assert b'name="documents"; filename="contract.pdf"' in body
    assert b"%PDF-1.4 fake" in body
    # caller-supplied idempotency key is honored
    assert request.headers["idempotency-key"] == "123e4567-e89b-12d3-a456-426614174000"


def test_fax_send_generates_uuid_idempotency_key(
    client: Client, mock_router: respx.Router
) -> None:
    route = mock_router.post("/v2.2/faxes").mock(
        return_value=httpx.Response(
            201, json=env({"id": "x", "fromNumber": "2015550123", "toNumber": "2125550123", "status": "queued", "documents": []})
        )
    )
    client.fax.send(
        from_number="2015550123",
        to_number="2125550123",
        documents=[FaxDocument("a.pdf", b"%PDF-")],
    )
    key = route.calls.last.request.headers["idempotency-key"]
    assert re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", key
    )


def test_fax_history(client: Client, mock_router: respx.Router) -> None:
    route = mock_router.get("/v2.2/faxes").mock(
        return_value=httpx.Response(
            200,
            json=env(
                {
                    "number": "2015550123",
                    "fromTs": 1795100000,
                    "toTs": 1795013600,
                    "faxes": [JOB],
                    "nextCursor": None,
                }
            ),
        )
    )
    result = client.fax.history(
        number="2015550123", from_ts=1795100000, to_ts=1795013600, limit=50, status="all"
    )
    assert isinstance(result, FaxHistoryData)
    assert result.faxes[0].status == "sent"
    assert result.faxes[0].documents[0].size == 123456
    assert result.nextCursor is None
    q = route.calls.last.request.url.params
    assert q["number"] == "2015550123"
    assert q["from"] == "1795100000" and q["to"] == "1795013600"
    assert q["limit"] == "50" and q["status"] == "all"


def test_fax_get_and_document(client: Client, mock_router: respx.Router) -> None:
    get_route = mock_router.get("/v2.2/faxes/9f8c2b41a").mock(
        return_value=httpx.Response(200, json=env(JOB))
    )
    doc_route = mock_router.get("/v2.2/faxes/9f8c2b41a/document").mock(
        return_value=httpx.Response(
            200,
            content=b"%PDF-1.4 binary-bytes",
            headers={"Content-Type": "application/pdf"},
        )
    )
    job = client.fax.get("9f8c2b41a")
    assert isinstance(job, FaxJob)
    assert job.documentAvailable is True
    assert job.attempts == 1
    assert get_route.called

    data = client.fax.document("9f8c2b41a")
    assert data == b"%PDF-1.4 binary-bytes"  # raw bytes, no envelope parsing
    assert doc_route.called


def test_fax_error_envelope_has_servertime(client: Client, mock_router: respx.Router) -> None:
    """Fax errors add serverTime beside the standard envelope — parse tolerantly."""
    from voicetel import VoiceTelError

    mock_router.get("/v2.2/faxes/deadbeef").mock(
        return_value=httpx.Response(
            404,
            json={
                "status": "error",
                "error": {"code": 404, "message": "Not found"},
                "serverTime": 1795100000,
            },
        )
    )
    try:
        client.fax.get("deadbeef")
        raise AssertionError("expected VoiceTelError")
    except VoiceTelError as exc:
        assert "Not found" in str(exc)


@pytest.mark.asyncio
async def test_fax_async(mock_router: respx.Router) -> None:
    mock_router.get("/v2.2/numbers/fax").mock(
        return_value=httpx.Response(200, json=env({"numbers": []}))
    )
    mock_router.get("/v2.2/faxes/9f8c2b41a/document").mock(
        return_value=httpx.Response(200, content=b"%PDF-", headers={"Content-Type": "application/pdf"})
    )
    async with AsyncClient(api_key="a" * 32, base_url=BASE, max_retries=0) as c:
        nums = await c.fax.list_numbers()
        assert nums.numbers == []
        doc = await c.fax.document("9f8c2b41a")
        assert doc == b"%PDF-"
