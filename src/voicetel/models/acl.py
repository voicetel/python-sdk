"""ACL (IP allowlist) models."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import CidrEntry

# ----------------------------------------------------------------- requests ---


class AclModifyRequest(_Base):
    """Body for POST /v2.2/acl (add) and DELETE /v2.2/acl (remove)."""

    acl: list[CidrEntry] = Field(description="CIDR entries to add or remove.")


# -------------------------------------------------- response data shapes ---


class AclListData(_Base):
    """Data payload from GET /v2.2/acl."""

    acl: list[CidrEntry] = Field(description="Current allowlist entries.")


class AclAddData(_Base):
    """Data payload from POST /v2.2/acl."""

    added: list[CidrEntry] = Field(description="Entries that were added.")


class AclRemoveData(_Base):
    """Data payload from DELETE /v2.2/acl."""

    removed: list[CidrEntry] = Field(description="Entries that were removed.")


AclFailureReason = Literal[
    "DB Insert failed",
    "DB delete failed",
    "Invalid mask: must be /8, /16, /24, or /32",
    "CIDR range must be routable",
]


class AclFailedEntry(_Base):
    """A CIDR that was rejected, with the reason. Appears in 409 conflict bodies."""

    cidr: str
    reason: AclFailureReason


class AclConflictData(_Base):
    """Data payload included in a 409 response from POST / DELETE /v2.2/acl.

    Surfaces *both* the entries that succeeded and the entries that failed, so the caller
    can reconcile partial outcomes.
    """

    added: list[CidrEntry] | None = None
    removed: list[CidrEntry] | None = None
    failed: list[AclFailedEntry] | None = None
