"""Shared building-block models referenced by multiple resources."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base


class CidrEntry(_Base):
    """A single CIDR row used by the ACL endpoint.

    Mask must be ``/8``, ``/16``, ``/24``, or ``/32`` and must describe a routable public address.
    """

    cidr: str = Field(description="IPv4 CIDR. Routable public; mask /8, /16, /24, or /32.")


class ErrorObject(_Base):
    """The ``error`` object inside :class:`ErrorResponse`."""

    code: int = Field(description="Machine-readable error code (mirrors the HTTP status).")
    message: str = Field(description="Free-form message text.")


class ErrorResponse(_Base):
    """Error envelope returned for non-2xx responses: ``{"status": "error", "error": {...}}``.

    Note that the SDK normally raises :class:`voicetel.ApiError` (or a subclass) rather than
    returning this directly; the model exists so callers can pattern-match on
    ``error.body`` when an :class:`~voicetel.ApiError` carries a JSON payload.
    """

    status: Literal["error"]
    error: ErrorObject
