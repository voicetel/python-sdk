"""Lookup-resource models — CNAM and LRN dips."""

from __future__ import annotations

from pydantic import Field

from ._base import PhoneNumber, _Base


class CnamData(_Base):
    """Data payload from GET /v2.2/cnam/{number}."""

    cnam: str | None = Field(default=None, description="Returned caller name, if available.")
    number: PhoneNumber = Field(description="The number that was queried.")


class LrnData(_Base):
    """LRN dip result. Returned both as the top-level data on GET /v2.2/lrn (when no ANI is
    provided) and nested inside :class:`LrnLookupData` when the full ``/lrn/{n}/{ani}`` form
    is called.
    """

    lrn: str | None = Field(default=None, description="Local Routing Number for the dipped TN.")
    state: str | None = Field(default=None, description="Two-letter US state code.")
    city: str | None = None
    rc: str | None = Field(default=None, description="Rate center.")
    lata: str | None = Field(default=None, description="LATA code.")
    ocn: str | None = Field(default=None, description="OCN of the carrier.")
    lec: str | None = Field(default=None, description="LEC name.")
    lecType: str | None = None
    jurisdiction: str | None = None
    local: str | None = Field(
        default=None,
        description="`Y`/`N` flag indicating whether the call is local to the ANI rate center.",
    )


class LrnLookupData(_Base):
    """Data payload from GET /v2.2/lrn/{number}/{ani}."""

    ani: PhoneNumber = Field(description="The presented ANI (passed in for billing/auth).")
    destination: PhoneNumber = Field(description="The dipped TN.")
    lrn: LrnData = Field(description="LRN data for the dipped TN.")
