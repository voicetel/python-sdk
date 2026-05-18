"""Authentication-resource models (SIP/HTTP auth mode + password)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import CidrEntry

# 0=Digest, 1=IP Auth, 2=Digest OR IP Auth, 3=Digest AND IP Auth
AuthType = Literal[0, 1, 2, 3]


# ----------------------------------------------------------------- requests ---


class AuthPutRequest(_Base):
    """PUT /v2.2/auth — update authentication mode and/or password."""

    authType: AuthType | None = Field(
        default=None,
        description="0=Digest, 1=IP Auth, 2=Digest OR IP, 3=Digest AND IP.",
    )
    password: str | None = Field(
        default=None,
        description="6-10 alphanumeric chars with at least one letter and one number.",
    )


# -------------------------------------------------- response data shapes ---


class AuthGetData(_Base):
    """Data payload from GET /v2.2/auth."""

    authType: AuthType = Field(description="Active auth mode.")
    authTypeDescription: str = Field(description="Human-readable label for ``authType``.")
    acl: list[CidrEntry] = Field(description="CIDR ranges authorized for IP-based auth.")


AuthUpdatedField = Literal["authType", "password"]


class AuthUpdatedEntry(_Base):
    """One field's change record, returned by PUT /v2.2/auth."""

    field: AuthUpdatedField
    value: int | None = Field(
        default=None,
        description="New value, when echoing is safe (e.g. authType). Omitted for password.",
    )


class AuthPutData(_Base):
    """Data payload from PUT /v2.2/auth."""

    updated: list[AuthUpdatedEntry] = Field(description="Fields that were changed.")


class AuthPutConflictData(_Base):
    """Data payload included in a conflict response from PUT /v2.2/auth.

    Same shape as :class:`AuthPutData` — conflicts surface which fields *would have* been
    updated alongside the rejected ones.
    """

    updated: list[AuthUpdatedEntry] | None = None
