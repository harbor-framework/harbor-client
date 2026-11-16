"""Public, contract-checked clients over Fern's generated resources."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
import logging
from typing import Any, Self, cast

import httpx
import requests

from .base_client import AsyncBaseHarborAPIClient, BaseHarborAPIClient
from .core.httpx_session import HttpxSession
from .net.environment import HarborAPIClientEnvironment
from .net.sdk_config import RetryConfig
from .validation import API_VERSION, DEFAULT_BASE_URL, _http


class _SessionTransport(httpx.BaseTransport):
    """Borrow an existing SDK-compatible session without owning its lifetime."""

    def __init__(self, session: Any, *, owns_adapter: bool = False):
        self.session = session
        self.owns_adapter = owns_adapter

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        timeout = request.extensions.get("timeout", {}).get("read", 60)
        response = self.session.request(
            request.method,
            str(request.url),
            headers=dict(request.headers),
            data=request.content,
            timeout=timeout,
            stream=False,
            allow_redirects=False,
        )
        try:
            headers = dict(response.headers)
            # Session responses are already decoded. Preserve their public headers
            # after constructing the buffered HTTPX response to avoid decoding twice.
            buffered = httpx.Response(
                response.status_code,
                headers={
                    k: v
                    for k, v in headers.items()
                    if k.lower() not in {"content-encoding", "content-length"}
                },
                content=response.content,
            )
            buffered.headers.update(headers)
            return buffered
        finally:
            response.close()

    def close(self) -> None:
        if self.owns_adapter:
            self.session.close()


class HarborAPIClient(BaseHarborAPIClient):
    """Use generated operations with checked wire payloads and one owned pool."""

    def __init__(
        self,
        *,
        token: str | Callable[[], str] | None = None,
        harbor_api_version: str = API_VERSION,
        base_url: HarborAPIClientEnvironment | str | None = None,
        environment: HarborAPIClientEnvironment | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        timeout_ms: int | None = None,
        http_client: requests.Session | None = None,
        httpx_client: httpx.Client | httpx.AsyncClient | None = None,
        follow_redirects: bool = True,
        logger: logging.Logger | None = None,
        retry: RetryConfig | None = None,
        stream_reconnection_enabled: bool | None = None,
        max_stream_reconnection_attempts: int | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        if (
            sum(value is not None for value in (http_client, httpx_client, transport))
            > 1
        ):
            raise ValueError("Choose one HTTP client or transport")
        selected = base_url if base_url is not None else environment
        url = (
            selected.value
            if isinstance(selected, HarborAPIClientEnvironment)
            else selected
        )
        if http_client is not None:
            transport = _SessionTransport(http_client)
        elif httpx_client is not None:
            transport = _SessionTransport(HttpxSession(httpx_client), owns_adapter=True)
        http = _http(url or DEFAULT_BASE_URL, transport)
        self._contract_http: httpx.Client | None = http
        try:
            super().__init__(
                token=token,
                harbor_api_version=harbor_api_version,
                base_url=base_url,
                environment=environment,
                headers=headers,
                timeout=timeout,
                timeout_ms=timeout_ms,
                httpx_client=http,
                follow_redirects=follow_redirects,
                logger=logger,
                retry=retry,
                stream_reconnection_enabled=stream_reconnection_enabled,
                max_stream_reconnection_attempts=max_stream_reconnection_attempts,
            )
        except BaseException:
            http.close()
            self._contract_http = None
            raise

    def __enter__(self) -> Self:
        return self

    def close(self) -> None:
        http, self._contract_http = self._contract_http, None
        if http is not None:
            http.close()
        super().close()


class AsyncHarborAPIClient(AsyncBaseHarborAPIClient, HarborAPIClient):
    """Async generated resources with the same checked construction contract."""

    def __init__(
        self,
        *,
        token: str | Callable[[], str] | None = None,
        harbor_api_version: str = API_VERSION,
        base_url: HarborAPIClientEnvironment | str | None = None,
        environment: HarborAPIClientEnvironment | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        timeout_ms: int | None = None,
        http_client: requests.Session | None = None,
        httpx_client: httpx.Client | httpx.AsyncClient | None = None,
        follow_redirects: bool = True,
        logger: logging.Logger | None = None,
        retry: RetryConfig | None = None,
        stream_reconnection_enabled: bool | None = None,
        max_stream_reconnection_attempts: int | None = None,
        async_token: Callable[[], Awaitable[str]] | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        if token is None and async_token is not None:
            token = cast(Callable[[], str], async_token)
        HarborAPIClient.__init__(
            self,
            token=token,
            harbor_api_version=harbor_api_version,
            base_url=base_url,
            environment=environment,
            headers=headers,
            timeout=timeout,
            timeout_ms=timeout_ms,
            http_client=http_client,
            httpx_client=httpx_client,
            follow_redirects=follow_redirects,
            logger=logger,
            retry=retry,
            stream_reconnection_enabled=stream_reconnection_enabled,
            max_stream_reconnection_attempts=max_stream_reconnection_attempts,
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def aclose(self) -> None:
        await asyncio.to_thread(self.close)
