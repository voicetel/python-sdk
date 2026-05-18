"""Base class shared by every model in this package.

Two policies:

- **Permissive on the way in.** ``extra="allow"`` lets the server add new fields without
  breaking validation. Clients pinned to today's models will simply ignore additions.
- **Tight on the way out.** :meth:`to_payload` serializes only the fields the caller
  explicitly set — important for PATCH/PUT bodies where ``None`` and "field not provided"
  must remain distinguishable.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

# Reusable pattern for ten-digit telephone numbers, as used throughout the API.
PhoneNumber = Annotated[str, Field(pattern=r"^[0-9]{10}$")]


class _Base(BaseModel):
    """Common Pydantic config for every model in this package."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )

    def to_payload(self) -> dict[str, Any]:
        """Render as a JSON-ready dict for the wire.

        Only fields the caller explicitly set are emitted — so a PATCH body that should
        contain just ``{"routeIn": 1}`` won't accidentally send ``{"routeIn": 1, "routeOut": null}``.
        """
        return self.model_dump(exclude_unset=True, by_alias=True, mode="json")
