"""e911-resource models.

Note the asymmetric ``dn`` patterns: requests take a 10-digit TN; responses return the
11-digit E.164 form (country code 1 prepended). This mirrors the OpenAPI spec exactly.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from ._base import PhoneNumber, _Base

# 11-digit E.164 US/CA form used in e911 responses (leading 1).
E164UsNumber = Annotated[str, Field(pattern=r"^1[2-9][0-9]{2}[2-9][0-9]{2}[0-9]{4}$")]
# 2-letter US state code.
StateCode = Annotated[str, Field(pattern=r"^[A-Z]{2}$")]


# ----------------------------------------------------------------- requests ---


class E911AddressRequest(_Base):
    """POST /v2.2/e911/validations — validate an address."""

    address1: str = Field(description="Street address line 1.")
    address2: str | None = Field(default=None, description="Apartment/suite/floor; may be empty.")
    city: str
    state: StateCode = Field(description="Two-letter US state code.")
    zip: str


class E911CreateRequest(_Base):
    """POST /v2.2/e911 — validate and provision in one call."""

    dn: PhoneNumber = Field(description="10-digit TN owned by the authenticated account.")
    callername: str = Field(description="Caller name displayed to dispatch.")
    address1: str
    address2: str | None = None
    city: str
    state: StateCode
    zip: str


class E911ProvisionByIdRequest(_Base):
    """PUT /v2.2/e911/{dn} — provision using a previously-validated addressId."""

    callername: str
    addressid: int = Field(description="From POST /v2.2/e911/validations.")


# -------------------------------------------------- entities & data shapes ---


class E911Entry(_Base):
    """An e911 record bound to a TN. Returned from GET/POST/PUT /v2.2/e911(/{dn})."""

    dn: E164UsNumber = Field(description="11-digit TN (E.164 US form, leading 1).")
    callername: str
    address1: str
    address2: str | None = None
    city: str
    state: StateCode
    zip: str


class E911ValidatedAddress(_Base):
    """Validation result from POST /v2.2/e911/validations.

    ``addressid`` is passed to :class:`E911ProvisionByIdRequest` to provision the address.
    """

    addressid: int = Field(description="Upstream address ID.")
    address1: str
    address2: str | None = None
    city: str
    state: StateCode
    zip: str


class E911AllData(_Base):
    """Data payload from GET /v2.2/e911."""

    records: list[E911Entry]


class E911RecordData(_Base):
    """Data payload from GET /v2.2/e911/{dn}."""

    record: E911Entry


class E911ValidateData(_Base):
    """Data payload from POST /v2.2/e911/validations."""

    address: E911ValidatedAddress
