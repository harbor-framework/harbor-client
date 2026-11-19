"""The root clients enforce the contract without a separate construction API."""

from contextlib import asynccontextmanager, contextmanager
import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

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
                200,
                json={
                    "items": [],
                    "total": invalid,
                    "next_cursor": None,
                    "prev_cursor": None,
                },
            )
        )
    ) as client:
        with pytest.raises(ContractError, match="response body"):
            list(client.jobs.list())


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_borrowed_httpx_pool_remains_open_and_retains_headers(asynchronous):
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(
            200,
            content=gzip.compress(
                json.dumps(
                    {"items": [], "total": 0, "next_cursor": None, "prev_cursor": None}
                ).encode()
            ),
            headers={"content-encoding": "gzip", "content-type": "application/json"},
        )

    pool = httpx.Client(
        transport=httpx.MockTransport(handler), headers={"X-Caller": "present"}
    )
    cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
    client = cls(token="key", httpx_client=pool, timeout=0.5)
    try:
        pager = client.jobs.list(cursor="opaque/+=token")
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
        assert seen[0].url.params["cursor"] == "opaque/+=token"
        assert seen[0].extensions["timeout"]["read"] == 0.5
    finally:
        client.close()
        pool.close()


@pytest.mark.parametrize("factory", [async_client, async_public])
async def test_async_entry_points_enforce_the_same_contract(factory):
    async with factory(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json={
                    "items": [],
                    "total": True,
                    "next_cursor": None,
                    "prev_cursor": None,
                },
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


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_borrowed_requests_session_retains_caller_ownership(asynchronous):
    import requests

    seen = []

    class Session(requests.Session):
        closed = False

        def request(self, method, url, **kwargs):
            seen.append((method, url, kwargs))
            response = requests.Response()
            response.status_code = 200
            response.headers["Content-Type"] = "application/json"
            response._content = (
                b'{"items": [], "total": 0, "next_cursor": null, "prev_cursor": null}'
            )
            return response

        def close(self):
            self.closed = True
            super().close()

    session = Session()
    client = (AsyncHarborAPIClient if asynchronous else HarborAPIClient)(
        token="key", http_client=session
    )
    try:
        if asynchronous:
            assert [item async for item in client.jobs.list()] == []
            await client.aclose()
        else:
            assert list(client.jobs.list()) == []
            client.close()
        assert not session.closed
        assert seen[0][2]["headers"]["authorization"] == "Bearer key"
    finally:
        client.close()
        session.close()


async def test_async_token_provider_works_through_the_public_constructor():
    async def token():
        return "async-token"

    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(
            200,
            json={"items": [], "total": 0, "next_cursor": None, "prev_cursor": None},
        )

    async with AsyncHarborAPIClient(
        async_token=token, transport=httpx.MockTransport(handler)
    ) as client:
        assert [item async for item in client.jobs.list()] == []
    assert seen[0].headers["Authorization"] == "Bearer async-token"


@contextmanager
def loopback(handler):
    """Serve handler(request_handler) on a real loopback socket."""
    seen = []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            seen.append(self.path)
            status, content_type, body = handler(len(seen))
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
    ).start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", seen
    finally:
        server.shutdown()
        server.server_close()


EMPTY_PAGE = json.dumps(
    {"items": [], "total": 0, "next_cursor": None, "prev_cursor": None}
).encode()
FAST_RETRY = {"attempts": 2, "delay_ms": 1, "max_delay_ms": 1}


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_plain_text_server_error_is_retried(asynchronous):
    def handler(call):
        if call == 1:
            return 500, "text/plain", b"upstream exploded"
        return 200, "application/json", EMPTY_PAGE

    with loopback(handler) as (url, seen):
        cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
        with cls(base_url=url, retry=FAST_RETRY) as client:
            pager = client.jobs.list()
            if asynchronous:
                assert [item async for item in pager] == []
            else:
                assert list(pager) == []
    assert seen == ["/v1/jobs", "/v1/jobs"]


@pytest.mark.parametrize(
    ("status", "content_type", "body"),
    [
        (404, "text/html", b"<html>proxy: not found</html>"),
        (502, "text/html", b"<html>bad gateway</html>"),
        (418, "application/json", b'{"undocumented": true}'),
    ],
)
def test_undocumented_error_bodies_raise_api_error(status, content_type, body):
    from harbor_client.core.api_error import ApiError

    with loopback(lambda _call: (status, content_type, body)) as (url, _seen):
        with HarborAPIClient(base_url=url, retry={"attempts": 0}) as client:
            with pytest.raises(ApiError) as caught:
                list(client.jobs.list())
    assert caught.value.status_code == status
    assert not isinstance(caught.value, ContractError)


def test_success_bodies_are_still_checked_strictly():
    with loopback(lambda _call: (200, "text/html", b"<html></html>")) as (url, _):
        with HarborAPIClient(base_url=url) as client:
            with pytest.raises(ValueError, match="content type"):
                list(client.jobs.list())


def test_set_base_url_moves_the_checked_pool():
    page = lambda _call: (200, "application/json", EMPTY_PAGE)  # noqa: E731
    with loopback(page) as (first, first_seen), loopback(page) as (second, seen):
        with HarborAPIClient(base_url=first) as client:
            assert list(client.jobs.list()) == []
            assert client.set_base_url(f"{second}/") is client
            assert list(client.jobs.list()) == []
            assert list(client.trials.list()) == []
            with pytest.raises(ValueError, match="HTTPS"):
                client.set_base_url("http://example.com")
    assert first_seen == ["/v1/jobs"]
    assert seen == ["/v1/jobs", "/v1/trials"]


@pytest.mark.parametrize("cls", [HarborAPIClient, AsyncHarborAPIClient])
async def test_borrowed_async_httpx_pool_is_rejected(cls):
    async with httpx.AsyncClient() as pool:
        with pytest.raises(TypeError, match="synchronous httpx.Client"):
            cls(httpx_client=pool)


@pytest.mark.parametrize("segment", ["..", "."])
def test_dot_path_parameters_never_reach_another_route(segment):
    sent = []
    with HarborAPIClient(
        transport=httpx.MockTransport(lambda request: sent.append(request))
    ) as client:
        with pytest.raises(ValueError, match="cannot be"):
            client.packages.get(organization_name=segment, name="jobs")
    assert sent == []


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_token_provider_returning_none_sends_no_authorization(asynchronous):
    sent = []

    def handler(request):
        sent.append(request)
        return httpx.Response(
            200,
            json={"items": [], "total": 0, "next_cursor": None, "prev_cursor": None},
        )

    tokens = iter(["first", None])
    transport = httpx.MockTransport(handler)
    if asynchronous:

        async def provider() -> str | None:
            return next(tokens)

        async with AsyncHarborAPIClient(async_token=provider, transport=transport) as c:
            for _ in range(2):
                _ = [item async for item in c.jobs.list()]
    else:
        with HarborAPIClient(token=lambda: next(tokens), transport=transport) as c:
            for _ in range(2):
                list(c.jobs.list())
    assert sent[0].headers["Authorization"] == "Bearer first"
    assert "Authorization" not in sent[1].headers


@pytest.mark.parametrize(
    ("status", "body"),
    [
        (
            404,
            {
                "_tag": "NotFound",
                "type": "about:blank",
                "title": "Not Found",
                "status": 404,
                "detail": "missing",
            },
        ),
        (418, {"undocumented": True}),
    ],
)
def test_api_error_string_omits_response_headers(status, body):
    from harbor_client.core.api_error import ApiError

    secrets = {
        "Set-Cookie": "session=COOKIE-SECRET",
        "Authorization": "Bearer AUTH-SECRET",
        "Content-Type": "application/problem+json",
    }
    with HarborAPIClient(
        token="key",
        retry={"attempts": 0},
        transport=httpx.MockTransport(
            lambda _: httpx.Response(status, json=body, headers=secrets)
        ),
    ) as client:
        with pytest.raises(ApiError) as caught:
            client.packages.get(organization_name="a", name="b")
    error = caught.value
    assert error.status_code == status
    assert error.headers is not None and error.headers["set-cookie"]
    for text in (str(error), repr(error)):
        assert "SECRET" not in text
    assert str(status) in str(error)


def test_request_and_response_strings_omit_credentials(monkeypatch):
    from harbor_client.net.transport.request import Request
    from harbor_client.services.utils.base_service import BaseService

    sent = []
    original = BaseService.send_request

    def capture(self, request):
        result = original(self, request)
        sent.append((request, self._last_response))
        return result

    monkeypatch.setattr(BaseService, "send_request", capture)
    with HarborAPIClient(
        token="AUTH-SECRET",
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                200,
                json={
                    "items": [],
                    "total": 0,
                    "next_cursor": None,
                    "prev_cursor": None,
                    "secret": "BODY-SECRET",
                },
                headers={"Set-Cookie": "session=COOKIE-SECRET"},
            )
        ),
    ) as client:
        list(client.jobs.list())
    request, response = sent[0]
    assert "AUTH-SECRET" in request.headers["Authorization"]
    assert "COOKIE-SECRET" in response.headers["Set-Cookie"]
    assert "BODY-SECRET" == response.body["secret"]
    assert "/v1/jobs" in str(request) and "GET" in str(request)
    assert "200" in str(response)
    for text in (str(request), str(response)):
        assert "SECRET" not in text

    upsert = Request()
    upsert.method, upsert.url = "PUT", "https://api.invalid/v1/secrets"
    upsert.headers = {"Authorization": "Bearer AUTH-SECRET"}
    upsert.body = {"value": "BODY-SECRET"}
    assert "SECRET" not in str(upsert)


@pytest.mark.parametrize(
    ("status", "tag", "title"),
    [
        (400, "BadRequest", "Bad Request"),
        (401, "Unauthorized", "Unauthorized"),
        (403, "Forbidden", "Forbidden"),
        (404, "NotFound", "Not Found"),
        (409, "Conflict", "Conflict"),
    ],
)
def test_api_error_string_shows_problem_detail(status, tag, title):
    from harbor_client.core.api_error import ApiError

    problem = {
        "_tag": tag,
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": "Job not found here",
    }
    with HarborAPIClient(
        retry={"attempts": 0},
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                status,
                json=problem,
                headers={"Content-Type": "application/problem+json"},
            )
        ),
    ) as client:
        with pytest.raises(ApiError) as caught:
            list(client.secrets.list())
    text = str(caught.value)
    # Typed (401/403/404) and untyped (400/409) problem bodies both show the detail.
    assert "Job not found here" in text
    assert f"{status}.0" not in text
