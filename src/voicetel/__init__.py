"""Official Python SDK for the VoiceTel REST API.

Quickstart::

    from voicetel import Client

    with Client() as c:
        c.login(username=1234567890, password="...")
        for n in c.numbers.list():
            print(n["number"])
"""

from __future__ import annotations

from . import models
from ._version import __version__
from .client import AsyncClient, Client
from .exceptions import (
    ApiError,
    AuthenticationError,
    BadRequestError,
    ConfigurationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    VoiceTelError,
)

__all__ = [
    "ApiError",
    "AsyncClient",
    "AuthenticationError",
    "BadRequestError",
    "Client",
    "ConfigurationError",
    "ConflictError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "ServerError",
    "VoiceTelError",
    "__version__",
    "models",
]
