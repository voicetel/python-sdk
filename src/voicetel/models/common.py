"""Shared building-block models referenced by multiple resources."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ._base import _Base


class CidrEntry(_Base):
    """A single CIDR row used by the ACL endpoint.

    Mask must be ``/8``, ``/16``, ``/24``, or ``/32`` and must describe a routable public address.
    """

    cidr: str = Field(description="IPv4 CIDR. Routable public; mask /8, /16, /24, or /32.")


class ErrorResponse(_Base):
    """Generic error envelope returned for non-2xx responses.

    Note that the SDK normally raises :class:`voicetel.ApiError` (or a subclass) rather than
    returning this directly; the model exists so callers can pattern-match on
    ``error.body`` when an :class:`~voicetel.ApiError` carries a JSON payload.
    """

    status: str | None = None
    code: str | None = None
    message: str | None = None
    error: str | None = None
    # Free-form payload — some error responses embed structured details.
    details: dict[str, Any] | None = None
