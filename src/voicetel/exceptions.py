from __future__ import annotations

from typing import Any


class VoiceTelError(Exception):
    """Base class for every error raised by this SDK."""


class ConfigurationError(VoiceTelError):
    """Raised when the client is constructed with conflicting or missing config."""


class ApiError(VoiceTelError):
    """Raised when the API returns a non-2xx response.

    Subclasses cover specific status families; catch :class:`ApiError` to handle them all.
    """

    status_code: int
    code: str | None
    body: Any

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.body = body

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code}, code={self.code!r})"


class BadRequestError(ApiError):
    """HTTP 400 — the request was malformed or failed server-side validation."""


class AuthenticationError(ApiError):
    """HTTP 401 — bearer token is missing, expired, or invalid."""


class PermissionDeniedError(ApiError):
    """HTTP 403 — authenticated, but not allowed to perform this action."""


class NotFoundError(ApiError):
    """HTTP 404 — the resource does not exist."""


class ConflictError(ApiError):
    """HTTP 409 — request conflicts with current resource state."""


class RateLimitError(ApiError):
    """HTTP 429 — too many requests. The `account/*` endpoints allow only 6 req/hour/IP."""


class ServerError(ApiError):
    """HTTP 5xx — the server hit an error processing the request."""


def from_response(status_code: int, code: str | None, body: Any, message: str) -> ApiError:
    """Map an HTTP status to the most specific :class:`ApiError` subclass."""
    cls: type[ApiError]
    if status_code == 400:
        cls = BadRequestError
    elif status_code == 401:
        cls = AuthenticationError
    elif status_code == 403:
        cls = PermissionDeniedError
    elif status_code == 404:
        cls = NotFoundError
    elif status_code == 409:
        cls = ConflictError
    elif status_code == 429:
        cls = RateLimitError
    elif 500 <= status_code < 600:
        cls = ServerError
    else:
        cls = ApiError
    return cls(message, status_code=status_code, code=code, body=body)
