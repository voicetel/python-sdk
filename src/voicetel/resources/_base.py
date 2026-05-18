from __future__ import annotations

from typing import Any

from .._http import AsyncTransport, Transport


def unwrap(envelope: Any) -> Any:
    """Strip the ``{"status": "success", "data": ...}`` wrapper if present.

    Some endpoints return the data inline (no envelope); those pass through unchanged.
    """
    if isinstance(envelope, dict) and "status" in envelope and "data" in envelope:
        return envelope["data"]
    return envelope


class Resource:
    """Mixin holding a sync :class:`Transport` reference."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport


class AsyncResource:
    """Mixin holding an :class:`AsyncTransport` reference."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport
