"""iNumbering-resource models — inventory, orders, ports."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import PhoneNumber, _Base

StreetDirection = Literal["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
NameType = Literal["business", "residential"]


# ----------------------------------------------------------------- requests ---


class OrderCreateRequest(_Base):
    """POST /v2.2/orders. ``numbers`` may be plain strings or objects with optional route."""

    numbers: list[PhoneNumber | OrderNumberSpec] = Field(
        max_length=100,
        min_length=1,
        description="Up to 100 numbers.",
    )


class OrderNumberSpec(_Base):
    """Per-number routing override inside :class:`OrderCreateRequest`."""

    number: PhoneNumber
    route: int | None = Field(
        default=None,
        description="Gateway ID on this account; defaults to 4.",
    )


OrderCreateRequest.model_rebuild()


class PortFeatureLidb(_Base):
    """LIDB feature for a port-in TN."""

    name: str = Field(max_length=15, description="Outbound caller name (max 15 chars).")


class PortFeatureRouting(_Base):
    """Routing feature for a port-in TN."""

    gatewayId: int


class PortFeatureSms(_Base):
    """SMS feature for a port-in TN."""

    campaignId: str | None = Field(default=None, description="10DLC campaign ID, e.g. C123456.")


class PortFeature(_Base):
    """Per-TN feature configuration applied after the port completes."""

    number: PhoneNumber
    routing: PortFeatureRouting | None = None
    lidb: PortFeatureLidb | None = None
    sms: PortFeatureSms | None = None


class PortSubmitRequest(_Base):
    """POST /v2.2/ports — submit a port-in order."""

    did: list[PhoneNumber] = Field(description="10-digit TNs to port (toll-free not supported).")
    name: str = Field(description="Subscriber name exactly as on the losing carrier bill.")
    nameType: NameType
    lcBtn: str = Field(description="Billing telephone number on the losing carrier bill.")
    lcAccountNumber: str = Field(description="Account number from the losing carrier bill.")
    streetNumber: str
    street: str = Field(description="Street name.")
    streetType: str = Field(description="USPS street type abbreviation (ST, AVE, BLVD, ...).")
    city: str
    state: str = Field(description="Two-letter state abbreviation.")
    zip: str
    country: str
    authPerson: str = Field(description="Full name authorised to sign the LOA.")
    streetPrefix: StreetDirection | None = None
    streetSuffix: StreetDirection | None = None
    floor: str | None = None
    room: str | None = None
    building: str | None = None
    unitValue: str | None = Field(
        default=None,
        description="Optional unit designator (e.g. 'APT 3' or 'STE 200').",
    )
    desiredDueDate: str | None = Field(
        default=None,
        description="Optional ISO 8601 desired port date. Blank = standard SLA.",
    )
    pin: str | None = Field(
        default=None,
        description="Optional port-out PIN required by the losing carrier.",
    )
    features: list[PortFeature] | None = None


# ----------------------------------------------------------- entities & data ---


class InventoryItem(_Base):
    """A single TN available for assignment."""

    number: PhoneNumber
    rateCenter: str = Field(description="Rate center name.")
    city: str
    province: str = Field(description="Two-letter state or province code.")
    lata: str = Field(description="LATA code.")


class InventoryCoverageItem(_Base):
    """One aggregated availability bucket. Which fields are populated depends on ``countBy``."""

    count: int = Field(description="Number of available TNs in this bucket.")
    npa: str | None = Field(default=None, description="Area code (countBy=npanxx).")
    nxx: str | None = Field(default=None, description="Exchange code (countBy=npanxx).")
    block: str | None = Field(default=None, description="Thousands-block (countBy=block).")
    city: str | None = Field(default=None, description="City name (countBy=city).")
    rcAbbre: str | None = Field(default=None, description="Rate center abbreviation (countBy=rateCenter).")
    lata: str | None = None
    locState: str | None = Field(default=None, description="State or province (countBy=state).")


class PortSummary(_Base):
    """One row in the customer port-status list."""

    status: str = Field(description="Port status, e.g. 'Complete'.")
    id: str | None = Field(default=None, description="Stable port record ID.")
    pid: str | None = Field(default=None, description="Short human-readable port reference.")
    foc: str | None = Field(default=None, description="Firm Order Commitment date (YYYYMMDD).")
    createdAt: str | None = None
    message: str | None = None
    supportUrl: str | None = Field(default=None, description="Related support ticket conversation URL.")


class PortDetail(_Base):
    """Full detail for a single port-in record."""

    status: str
    id: str | None = None
    pid: str | None = None
    name: str | None = Field(default=None, description="Account name on the port.")
    email: str | None = Field(default=None, description="Notification email at submission.")
    foc: str | None = None
    createdAt: str | None = None
    numbers: list[str] | None = None
    message: str | None = None


# ----------------------------------------------------------- data shapes ---


class InventorySearchData(_Base):
    """Data payload from GET /v2.2/inventory."""

    numbers: list[InventoryItem]


class InventoryCoverageData(_Base):
    """Data payload from GET /v2.2/inventory/coverage."""

    coverage: list[InventoryCoverageItem]


class OrderFailedEntry(_Base):
    """One row in :attr:`OrderCreateData.failed`."""

    number: PhoneNumber
    reason: str


class OrderCreateData(_Base):
    """Data payload from POST /v2.2/orders."""

    orderId: str
    amountCharged: float = Field(description="USD deducted from accounts.cash.")
    numbersOrdered: list[str] = Field(description="Numbers inserted into the account on success.")
    failed: list[OrderFailedEntry] = Field(default_factory=list)


class PortListData(_Base):
    """Data payload from GET /v2.2/ports."""

    ports: list[PortSummary]


class PortDetailData(_Base):
    """Data payload from GET /v2.2/ports/{id}."""

    port: PortDetail


class PortSubmitData(_Base):
    """Data payload from POST /v2.2/ports."""

    pid: str = Field(description="5-character port order ID.")
    ticket: int = Field(description="Support ticket ID.")
    message: str
    loaUrl: str = Field(description="URL to download and sign the LOA.")
    portUrl: str = Field(description="URL to track port order status.")


class PortAvailabilityData(_Base):
    """Data payload from GET /v2.2/ports/availability/{number}."""

    number: PhoneNumber
    portable: bool
    losingCarrier: str | None = Field(
        default=None,
        description=(
            "Service provider name currently providing this number, when the "
            "network supplies it. Null when the network can't identify a provider."
        ),
    )
    localRoutingNumber: PhoneNumber | None = Field(
        default=None,
        description=(
            "Local Routing Number assigned to the destination switch, when the "
            "network reports it. Null when not available. (Added in v2.2.10.)"
        ),
    )
    rateCenterTier: str | None = Field(
        default=None,
        description=(
            "Rate-center tier classification reported by the network. "
            "Null when not available. (Added in v2.2.10.)"
        ),
    )
    reason: str | None = Field(
        default=None,
        description=(
            "When ``portable`` is False, the network-supplied reason. "
            "Null when ``portable`` is True."
        ),
    )
