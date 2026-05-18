from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ._version import __version__
from .exceptions import ApiError, ConfigurationError, from_response

DEFAULT_BASE_URL = "https://api.voicetel.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_USER_AGENT = f"voicetel-python/{__version__} (+https://github.com/voicetel/python-sdk)"

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class Transport:
    """Sync HTTP transport. Owns an :class:`httpx.Client` and the retry/auth policy.

    The Bearer token is mutable: :meth:`set_bearer` lets the auth flow swap it in after the
    api-key exchange runs.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        if max_retries < 0:
            raise ConfigurationError("max_retries must be >= 0")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._user_agent = user_agent
        self._owns_client = http_client is None
        self._http: httpx.Client = http_client or httpx.Client(
            base_url=self._base_url, timeout=timeout
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_key(self) -> str | None:
        return self._api_key

    def set_bearer(self, api_key: str) -> None:
        self._api_key = api_key

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        require_auth: bool = True,
    ) -> Any:
        headers = self._headers(require_auth=require_auth)
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = self._http.request(
                    method,
                    path,
                    params=_clean_params(params),
                    json=json,
                    headers=headers,
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise ApiError(
                        f"transport error after {attempt + 1} attempts: {exc}",
                        status_code=0,
                    ) from exc
                _sleep_backoff(attempt)
                continue
            if response.status_code in _RETRYABLE_STATUSES and attempt < self._max_retries:
                _sleep_backoff(attempt, response)
                continue
            return _parse(response)
        # unreachable: the loop always returns or raises
        assert last_exc is not None  # pragma: no cover
        raise last_exc  # pragma: no cover

    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> Transport:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def _headers(self, *, require_auth: bool) -> dict[str, str]:
        headers = {"User-Agent": self._user_agent, "Accept": "application/json"}
        if require_auth:
            if not self._api_key:
                raise ConfigurationError(
                    "no api_key set; pass api_key= to Client(...) or call client.login()"
                )
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers


class AsyncTransport:
    """Async counterpart to :class:`Transport`. Same surface, awaitable :meth:`request`."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        if max_retries < 0:
            raise ConfigurationError("max_retries must be >= 0")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._user_agent = user_agent
        self._owns_client = http_client is None
        self._http: httpx.AsyncClient = http_client or httpx.AsyncClient(
            base_url=self._base_url, timeout=timeout
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_key(self) -> str | None:
        return self._api_key

    def set_bearer(self, api_key: str) -> None:
        self._api_key = api_key

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        require_auth: bool = True,
    ) -> Any:
        headers = self._headers(require_auth=require_auth)
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._http.request(
                    method,
                    path,
                    params=_clean_params(params),
                    json=json,
                    headers=headers,
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise ApiError(
                        f"transport error after {attempt + 1} attempts: {exc}",
                        status_code=0,
                    ) from exc
                await asyncio.sleep(_backoff_delay(attempt))
                continue
            if response.status_code in _RETRYABLE_STATUSES and attempt < self._max_retries:
                await asyncio.sleep(_backoff_delay(attempt, response))
                continue
            return _parse(response)
        assert last_exc is not None  # pragma: no cover
        raise last_exc  # pragma: no cover

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()

    def _headers(self, *, require_auth: bool) -> dict[str, str]:
        headers = {"User-Agent": self._user_agent, "Accept": "application/json"}
        if require_auth:
            if not self._api_key:
                raise ConfigurationError(
                    "no api_key set; pass api_key= to AsyncClient(...) or call client.login()"
                )
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _parse(response: httpx.Response) -> Any:
    if 200 <= response.status_code < 300:
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(
                f"non-JSON success response: {response.text[:200]}",
                status_code=response.status_code,
                body=response.text,
            ) from exc
    body: Any
    try:
        body = response.json()
    except ValueError:
        body = response.text
    code = None
    message = f"HTTP {response.status_code}"
    if isinstance(body, dict):
        code = body.get("code") or body.get("error")
        message = body.get("message") or body.get("error") or message
    raise from_response(response.status_code, code, body, message)


def _backoff_delay(attempt: int, response: httpx.Response | None = None) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                pass
    return float(min(8.0, 0.5 * (2**attempt)))


def _sleep_backoff(attempt: int, response: httpx.Response | None = None) -> None:
    time.sleep(_backoff_delay(attempt, response))
