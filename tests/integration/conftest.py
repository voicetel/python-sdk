"""Integration-test fixtures.

These tests hit the live VoiceTel API at ``VOICETEL_BASE_URL`` (default ``https://api.voicetel.com``).
They are skipped automatically unless both ``VOICETEL_USERNAME`` and ``VOICETEL_PASSWORD`` are
set in the environment.

By convention, integration tests in this directory only exercise **read-only** endpoints. The
``api-key`` exchange used to obtain a session bearer counts against the 6 req/hour/IP limit, so
the bearer is cached at session scope and re-used across tests.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from voicetel import AsyncClient, Client


def _load_dotenv() -> None:
    """Minimal .env loader — looks for python/.env and pushes KEY=VAL pairs into os.environ.

    Avoids the python-dotenv dependency for a 10-line task.
    """
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

USERNAME = os.environ.get("VOICETEL_USERNAME")
PASSWORD = os.environ.get("VOICETEL_PASSWORD")
BASE_URL = os.environ.get("VOICETEL_BASE_URL", "https://api.voicetel.com")

_skip_no_creds = pytest.mark.skipif(
    not (USERNAME and PASSWORD),
    reason="VOICETEL_USERNAME and VOICETEL_PASSWORD must be set to run integration tests",
)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark every test in this directory as `integration` and skip without creds."""
    integration_dir = Path(__file__).parent.resolve()
    for item in items:
        if integration_dir in Path(item.fspath).parents:
            item.add_marker(pytest.mark.integration)
            item.add_marker(_skip_no_creds)


@pytest.fixture(scope="session")
def api_key() -> str:
    """Exchange username/password for a session API key — burns 1 of 6 hourly slots."""
    assert USERNAME and PASSWORD  # _skip_no_creds guarantees this at collection time
    with Client(base_url=BASE_URL, max_retries=0) as c:
        return c.login(int(USERNAME) if USERNAME.isdigit() else USERNAME, PASSWORD)


@pytest.fixture
def client(api_key: str):
    with Client(api_key=api_key, base_url=BASE_URL) as c:
        yield c


@pytest.fixture
def aclient(api_key: str):
    async def _factory():
        return AsyncClient(api_key=api_key, base_url=BASE_URL)

    return _factory
