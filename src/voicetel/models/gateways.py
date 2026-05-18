"""Gateway-resource models — outbound termination routes."""

from __future__ import annotations

from pydantic import Field

from ._base import PhoneNumber, _Base

# ----------------------------------------------------------------- requests ---


class GatewayAddRequest(_Base):
    """POST /v2.2/gateways."""

    gateway: str = Field(
        description=(
            "IP or hostname with optional ``:port``; "
            "must resolve to a routable public IPv4."
        )
    )
    prefix: str | None = Field(default=None, description="Digits to prepend on outbound calls.")
    limit: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Max concurrent calls. Default: 23.",
    )


class GatewayUpdateRequest(_Base):
    """PUT /v2.2/gateways/{id}."""

    gateway: str | None = None
    prefix: str | None = None
    limit: int | None = Field(default=None, ge=1, le=1000)


# -------------------------------------------------- entities & response data ---


class GatewayEntry(_Base):
    """A single gateway row."""

    id: int | None = Field(default=None, description="Gateway ID.")
    gateway: str | None = Field(
        default=None,
        description="Gateway IP:port or system route name (USER, T30, etc.)",
    )
    prefix: str | None = Field(default=None, description="Digits prepended to outbound calls.")
    limit: int | None = Field(
        default=None,
        description="Max concurrent calls. Null for system routes.",
    )
    system: bool | None = Field(
        default=None,
        description="True for built-in system route types.",
    )


class GatewayNumberSummary(_Base):
    """One number bound to a gateway, as returned by GET /v2.2/gateways/{id}/numbers."""

    number: PhoneNumber
    translated: PhoneNumber = Field(
        description="Destination after translation rewrite — usually equal to ``number``.",
    )
    forward: bool = Field(description="True when call forwarding is enabled.")
    forwardTo: str | None = Field(description="Forwarding destination when ``forward`` is true.")
    cnam: bool = Field(description="True when inbound CNAM lookup is enabled.")
    carrier: int = Field(description="Outbound messaging carrier id; 0 = none.")
    smsEnabled: bool
    faxEnabled: bool


class GatewaysListData(_Base):
    """Data payload from GET /v2.2/gateways."""

    gateways: list[GatewayEntry]


class GatewayNumbersData(_Base):
    """Data payload from GET /v2.2/gateways/{id}/numbers."""

    numbers: list[GatewayNumberSummary]
