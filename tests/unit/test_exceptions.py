from __future__ import annotations

import pytest

from voicetel.exceptions import (
    ApiError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    from_response,
)


@pytest.mark.parametrize(
    ("status", "cls"),
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (403, PermissionDeniedError),
        (404, NotFoundError),
        (409, ConflictError),
        (429, RateLimitError),
        (500, ServerError),
        (502, ServerError),
        (599, ServerError),
        (418, ApiError),
        (200, ApiError),
    ],
)
def test_from_response_maps_status_to_subclass(status: int, cls: type[ApiError]) -> None:
    err = from_response(status, "EX", {"k": 1}, "boom")
    assert type(err) is cls
    assert err.status_code == status
    assert err.code == "EX"
    assert err.body == {"k": 1}
    assert str(err) == "boom"


def test_error_repr_includes_status_and_code() -> None:
    err = ApiError("nope", status_code=500, code="X")
    assert "500" in repr(err) and "X" in repr(err)


def test_error_defaults() -> None:
    err = ApiError("nope", status_code=500)
    assert err.code is None
    assert err.body is None
