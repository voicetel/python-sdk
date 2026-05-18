from __future__ import annotations

from typing import Any

import httpx

from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncTransport,
    Transport,
)
from .auth import aexchange_api_key, exchange_api_key
from .resources import (
    AccountAsyncResource,
    AccountResource,
    AclAsyncResource,
    AclResource,
    AuthenticationAsyncResource,
    AuthenticationResource,
    E911AsyncResource,
    E911Resource,
    GatewaysAsyncResource,
    GatewaysResource,
    INumberingAsyncResource,
    INumberingResource,
    LookupsAsyncResource,
    LookupsResource,
    MessagingAsyncResource,
    MessagingResource,
    NumbersAsyncResource,
    NumbersResource,
    SupportAsyncResource,
    SupportResource,
)


class Client:
    """Synchronous client for the VoiceTel REST API.

    Construct with an existing ``api_key`` or call :meth:`login` to exchange username/password.
    All resource groups are exposed as attributes (``client.numbers``, ``client.account``, ...).

    Usage as a context manager closes the underlying ``httpx.Client``::

        with Client(api_key=key) as c:
            account = c.account.get()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._transport = Transport(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.account = AccountResource(self._transport)
        self.acl = AclResource(self._transport)
        self.authentication = AuthenticationResource(self._transport)
        self.e911 = E911Resource(self._transport)
        self.gateways = GatewaysResource(self._transport)
        self.inumbering = INumberingResource(self._transport)
        self.lookups = LookupsResource(self._transport)
        self.messaging = MessagingResource(self._transport)
        self.numbers = NumbersResource(self._transport)
        self.support = SupportResource(self._transport)

    @property
    def api_key(self) -> str | None:
        return self._transport.api_key

    @property
    def base_url(self) -> str:
        return self._transport.base_url

    def login(self, username: int | str, password: str) -> str:
        """Exchange username/password for an API key and install it. Returns the new key."""
        return exchange_api_key(self._transport, username, password)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


class AsyncClient:
    """Async counterpart to :class:`Client`. Same surface; methods are awaitable.

    Use as an async context manager::

        async with AsyncClient(api_key=key) as c:
            account = await c.account.get()
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._transport = AsyncTransport(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.account = AccountAsyncResource(self._transport)
        self.acl = AclAsyncResource(self._transport)
        self.authentication = AuthenticationAsyncResource(self._transport)
        self.e911 = E911AsyncResource(self._transport)
        self.gateways = GatewaysAsyncResource(self._transport)
        self.inumbering = INumberingAsyncResource(self._transport)
        self.lookups = LookupsAsyncResource(self._transport)
        self.messaging = MessagingAsyncResource(self._transport)
        self.numbers = NumbersAsyncResource(self._transport)
        self.support = SupportAsyncResource(self._transport)

    @property
    def api_key(self) -> str | None:
        return self._transport.api_key

    @property
    def base_url(self) -> str:
        return self._transport.base_url

    async def login(self, username: int | str, password: str) -> str:
        return await aexchange_api_key(self._transport, username, password)

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
