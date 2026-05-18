from __future__ import annotations

import pytest
import respx

from voicetel import AsyncClient, Client

TEST_API_KEY = "0" * 32
TEST_BASE_URL = "https://api.voicetel.test"


@pytest.fixture
def client() -> Client:
    return Client(api_key=TEST_API_KEY, base_url=TEST_BASE_URL, max_retries=0)


@pytest.fixture
def aclient() -> AsyncClient:
    return AsyncClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL, max_retries=0)


@pytest.fixture
def mock_router():
    """Yields a respx router with both base URLs registered so sync and async work."""
    with respx.mock(base_url=TEST_BASE_URL, assert_all_called=False) as router:
        yield router


def ok(data: object | None = None) -> dict[str, object]:
    """Build a standard ``{"status":"success","data":...}`` envelope."""
    return {"status": "success", "data": data if data is not None else {}}
