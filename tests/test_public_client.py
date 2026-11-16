"""The root clients enforce the contract without a separate construction API."""

from contextlib import asynccontextmanager, contextmanager
import gzip
import json

import httpx
import pytest

from harbor_client import AsyncHarborAPIClient, HarborAPIClient
from harbor_client.validation import (
    API_VERSION,
    ContractError,
    async_client,
    sync_client,
)


@contextmanager
def sync_public(**kwargs):
    with HarborAPIClient(**kwargs) as client:
        yield client


@asynccontextmanager
async def async_public(**kwargs):
    async with AsyncHarborAPIClient(**kwargs) as client:
        yield client


@pytest.mark.parametrize("factory", [sync_client, sync_public])
@pytest.mark.parametrize("invalid", [True, "0", None])
def test_public_and_compatibility_clients_reject_invalid_wire_fields(factory, invalid):
    with factory(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200, json={"items": [], "total": invalid, "next_page_token": ""}
            )
        )
    ) as client:
        with pytest.raises(ContractError, match="response body"):
            list(client.jobs.list())


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("borrowed_async", [False, True])
async def test_borrowed_httpx_pool_remains_open_and_retains_headers(
    asynchronous, borrowed_async
):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(
            200,
            content=gzip.compress(
                json.dumps({"items": [], "total": 0, "next_page_token": ""}).encode()
            ),
            headers={"content-encoding": "gzip", "content-type": "application/json"},
        )

    pool_class = httpx.AsyncClient if borrowed_async else httpx.Client
    pool = pool_class(
        transport=httpx.MockTransport(handler), headers={"X-Caller": "present"}
    )
    cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
    client = cls(token="key", httpx_client=pool, timeout=0.5)
    try:
        pager = client.jobs.list(page_token="opaque/+=token")
        if asynchronous:
            assert [item async for item in pager] == []
            await client.aclose()
            await client.aclose()
        else:
            assert list(pager) == []
            client.close()
            client.close()
        assert not pool.is_closed
        assert len(seen) == 1
        assert seen[0].headers["X-Caller"] == "present"
        assert seen[0].headers["Harbor-API-Version"] == API_VERSION
        assert seen[0].headers["Authorization"] == "Bearer key"
        assert seen[0].url.params["page_token"] == "opaque/+=token"
        assert seen[0].extensions["timeout"]["read"] == 0.5
    finally:
        client.close()
        if borrowed_async:
            await pool.aclose()
        else:
            pool.close()


@pytest.mark.parametrize("factory", [async_client, async_public])
async def test_async_entry_points_enforce_the_same_contract(factory):
    async with factory(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200, json={"items": [], "total": True, "next_page_token": ""}
            )
        )
    ) as client:
        with pytest.raises(ContractError):
            _ = [item async for item in client.jobs.list()]


def test_root_exports_include_support_types_and_established_environment_name():
    from harbor_client import (
        ContractError as RootError,
        HarborAPIClientEnvironment,
        StorageTransferError,
        UploadFile,
    )
    from harbor_client.net.environment import HarborAPIClientEnvironment as Environment
    from harbor_client.transfers import (
        StorageTransferError as TransferError,
        UploadFile as File,
    )

    assert RootError is ContractError
    assert TransferError is StorageTransferError
    assert UploadFile is File
    assert HarborAPIClientEnvironment is Environment
    with HarborAPIClient(
        environment=Environment.DEFAULT,
        transport=httpx.MockTransport(lambda _: pytest.fail("No request expected")),
    ):
        pass
