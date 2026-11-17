"""Exercise workflow boundaries, streaming, recovery, and credential isolation."""

from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import tarfile
import threading
import time

import httpx
import pytest

from harbor_client.transfers import (
    AsyncStorageTransfers,
    StorageTransferError,
    StorageTransfers,
    UploadFile,
)

pytestmark = pytest.mark.unit


def grant(method="GET", **extra):
    return {
        "protocol": "http",
        "method": method,
        "url": "https://storage.invalid/object?token=secret",
        "headers": {"x-signed-capability": "object-only"},
        "expires_at": "2099-01-01T00:00:00Z",
        **extra,
    }


class Api:
    def __init__(self):
        self.calls = []
        self.download = grant(size_bytes=5)
        self.state = "pending"
        self.storage = self
        self.packages = self
        self.jobs = self
        self.trials = self

    def create_upload(self, *, request):
        self.calls.append(("prepare", request))
        return {
            "id": "upload",
            "state": self.state,
            "files": [
                {**file, "id": str(index), "upload": grant("PUT")}
                for index, file in enumerate(request["files"])
            ],
        }

    def complete_upload(self, **request):
        self.calls.append(("complete", request))
        return {
            "id": "upload",
            "state": "completed",
            "result": {"resource_id": "resource"},
        }

    def get_artifact_download(self, **request):
        self.calls.append(("download", request))
        return self.download

    download_file = get_artifact_download
    download_archive = get_artifact_download

    def copy(self, **request):
        self.calls.append(("copy", request.copy()))
        return {
            "complete": len([call for call in self.calls if call[0] == "copy"]) >= 2,
            "n_copied": 1,
        }


class AsyncApi:
    def __init__(self, api):
        self.api = api
        self.storage = self
        self.packages = self
        self.jobs = self
        self.trials = self

    def __getattr__(self, name):
        async def call(**kwargs):
            return getattr(self.api, name)(**kwargs)

        return call


def safe_headers(request):
    assert request.headers.get("authorization") is None
    assert request.headers.get("apikey") is None
    assert request.headers.get("cookie") is None
    assert request.headers.get("Harbor-API-Version") is None
    assert request.headers["x-signed-capability"] == "object-only"


def test_upload_drives_prepare_transfer_complete_without_provider_sdk(tmp_path):
    source = tmp_path / "data"
    source.write_bytes(b"bytes")
    api = Api()
    seen = []

    def handler(request):
        safe_headers(request)
        seen.append(request.read())
        return httpx.Response(200)

    client = StorageTransfers(api, transport=httpx.MockTransport(handler))
    assert (
        client.upload(
            kind="task",
            request_id="same-on-retry",
            metadata={"name": "task"},
            files=[UploadFile("dist.tar.gz", source, "archive")],
        )["state"]
        == "completed"
    )
    assert seen == [b"bytes"]
    assert [call[0] for call in api.calls] == ["prepare", "complete"]
    assert api.calls[0][1]["files"][0] == {
        "path": "dist.tar.gz",
        "role": "archive",
        "size_bytes": 5,
        "sha256": hashlib.sha256(b"bytes").hexdigest(),
    }


def test_failed_upload_never_publishes_and_does_not_leak_signed_url(tmp_path):
    source = tmp_path / "data"
    source.write_bytes(b"bytes")
    api = Api()
    client = StorageTransfers(
        api,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(403, text="token=secret")
        ),
    )
    with pytest.raises(StorageTransferError) as caught:
        client.upload(
            kind="task",
            request_id="retry",
            metadata={},
            files=[UploadFile("file", source)],
        )
    assert caught.value.upload_id == "upload"
    assert caught.value.status_code == 403
    assert "secret" not in str(caught.value)
    assert [call[0] for call in api.calls] == ["prepare"]
    # If a transfer succeeded but its response was lost, callers can directly
    # retry the API's verification/publication step without re-PUTing bytes.
    assert client.complete_upload("upload")["state"] == "completed"


@pytest.mark.parametrize("state", ["verified", "completed"])
def test_verified_upload_does_not_replay_put(tmp_path, state):
    source = tmp_path / "data"
    source.write_bytes(b"bytes")
    api = Api()
    api.state = state

    def handler(request):
        pytest.fail("A completed upload must not replay a signed PUT")

    client = StorageTransfers(api, transport=httpx.MockTransport(handler))
    assert (
        client.upload(
            kind="task",
            request_id="retry",
            metadata={},
            files=[UploadFile("file", source)],
        )["state"]
        == "completed"
    )


def test_download_isolated_stream_and_atomic_replacement(tmp_path):
    api = Api()

    def handler(request):
        safe_headers(request)
        return httpx.Response(200, stream=httpx.ByteStream(b"bytes"))

    target = tmp_path / "artifact"
    target.write_bytes(b"old")
    client = StorageTransfers(api, transport=httpx.MockTransport(handler))
    assert (
        client.download(
            kind="trial", resource_id="id", role="archive", destination=target
        )
        == target
    )
    assert target.read_bytes() == b"bytes"
    api.download["size_bytes"] = 100
    with pytest.raises(StorageTransferError, match="size"):
        client.download(
            kind="trial", resource_id="id", role="archive", destination=target
        )
    assert target.read_bytes() == b"bytes"
    assert list(tmp_path.iterdir()) == [target]


def archive_bytes(*, symlink=False):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        info = tarfile.TarInfo("folder/file.txt")
        if symlink:
            info.type = tarfile.SYMTYPE
            info.linkname = "/etc/passwd"
            archive.addfile(info)
        else:
            info.size = 5
            archive.addfile(info, io.BytesIO(b"bytes"))
    return output.getvalue()


@pytest.mark.parametrize("symlink", [False, True])
def test_bundled_package_download_never_extracts_links(tmp_path, symlink):
    data = archive_bytes(symlink=symlink)
    api = Api()
    api.download = grant(size_bytes=len(data), archive_member="folder/file.txt")
    client = StorageTransfers(
        api,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=httpx.ByteStream(data))
        ),
    )
    target = tmp_path / "file"
    if symlink:
        with pytest.raises(StorageTransferError, match="regular file"):
            client.download(
                kind="task",
                resource_id="id",
                role="file",
                path="folder/file.txt",
                destination=target,
            )
        assert not target.exists()
    else:
        client.download(
            kind="task",
            resource_id="id",
            role="file",
            path="folder/file.txt",
            destination=target,
        )
        assert target.read_bytes() == b"bytes"


def test_copy_overwrite_only_on_first_pass():
    api = Api()
    rounds = []
    result = StorageTransfers(api).copy(
        kind="job", source_id="source", overwrite=True, on_round=rounds.append
    )
    assert result["complete"] and result["n_copied"] == 2
    assert [item["n_copied"] for item in rounds] == [1, 1]
    assert [call[1]["overwrite"] for call in api.calls] == [True, False]
    assert all(call[1]["source_job_id"] == "source" for call in api.calls)
    with pytest.raises(ValueError):
        StorageTransfers(api).copy(kind="job", source_id="source", max_passes=0)


def test_copy_returns_incomplete_when_bounded_or_unable_to_progress():
    assert not StorageTransfers(Api()).copy(
        kind="trial", source_id="source", max_passes=1
    )["complete"]

    class NoProgressApi(Api):
        def copy(self, **request):
            result = super().copy(**request)
            return {**result, "n_copied": 0}

    api = NoProgressApi()
    result = StorageTransfers(api).copy(kind="trial", source_id="source")
    assert not result["complete"] and result["n_copied"] == 0
    assert len(api.calls) == 1


def test_empty_dataset_upload_still_completes():
    api = Api()
    receipt = StorageTransfers(api).upload(
        kind="dataset", request_id="empty", metadata={"tasks": []}, files=[]
    )
    assert receipt["state"] == "completed"
    assert [name for name, _ in api.calls] == ["prepare", "complete"]


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_optional_trajectory_transfer_failure_still_verifies_archive(
    tmp_path, asynchronous
):
    source = tmp_path / "input"
    source.write_bytes(b"bytes")
    api = Api()
    calls = []

    def handler(request):
        calls.append(request.method)
        return httpx.Response(200 if len(calls) == 1 else 503)

    args = {
        "kind": "trial",
        "request_id": "retry",
        "metadata": {},
        "files": [
            UploadFile("archive", source, "archive"),
            UploadFile("trajectory", source, "trajectory", optional=True),
        ],
    }
    if asynchronous:
        client = AsyncStorageTransfers(
            AsyncApi(api), transport=httpx.MockTransport(handler)
        )
        receipt = await client.upload(**args)
    else:
        receipt = StorageTransfers(api, transport=httpx.MockTransport(handler)).upload(
            **args
        )
    assert receipt["state"] == "completed"
    assert len(calls) == 2
    assert api.calls[0][1]["files"][1]["optional"] is True
    assert [name for name, _ in api.calls] == ["prepare", "complete"]


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_racing_put_conflict_always_reaches_authoritative_verification(
    tmp_path, asynchronous
):
    class VerifyApi(Api):
        def complete_upload(self, **request):
            super().complete_upload(**request)
            raise RuntimeError("Backend verification rejected existing bytes")

    source = tmp_path / "input"
    source.write_bytes(b"bytes")
    api = VerifyApi()
    transport = httpx.MockTransport(lambda request: httpx.Response(409))
    args = {
        "kind": "trial",
        "request_id": "retry",
        "metadata": {},
        "files": [UploadFile("archive", source, "archive")],
    }
    with pytest.raises(RuntimeError, match="verification rejected"):
        if asynchronous:
            await AsyncStorageTransfers(AsyncApi(api), transport=transport).upload(
                **args
            )
        else:
            StorageTransfers(api, transport=transport).upload(**args)
    assert [name for name, _ in api.calls] == ["prepare", "complete"]


@pytest.mark.parametrize(
    "kind,role,path,attribution,expected",
    [
        (
            "task",
            "archive",
            None,
            {"transfer_id": "transfer", "dataset_version_id": "dataset"},
            {
                "version_id": "id",
                "transfer_id": "transfer",
                "dataset_version_id": "dataset",
            },
        ),
        (
            "task",
            "file",
            "instruction.md",
            {},
            {"version_id": "id", "file": "instruction.md"},
        ),
        (
            "dataset",
            "file",
            "metric.py",
            {"transfer_id": "transfer"},
            {"version_id": "id", "file": "metric.py", "transfer_id": "transfer"},
        ),
        ("job", "log", None, {}, {"job_id": "id", "artifact_type": "log"}),
        (
            "trial",
            "trajectory",
            None,
            {},
            {"trial_id": "id", "artifact_type": "trajectory"},
        ),
    ],
)
def test_download_uses_resource_methods_and_preserves_attribution(
    tmp_path, kind, role, path, attribution, expected
):
    api = Api()
    client = StorageTransfers(
        api,
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, stream=httpx.ByteStream(b"bytes"))
        ),
    )
    client.download(
        kind=kind,
        resource_id="id",
        role=role,
        path=path,
        destination=tmp_path / "new" / "file",
        **attribution,
    )
    assert api.calls == [("download", expected)]


async def test_async_upload_download_and_copy(tmp_path):
    source = tmp_path / "input"
    source.write_bytes(b"bytes")
    api = Api()

    async def handler(request):
        safe_headers(request)
        if request.method == "PUT":
            assert await request.aread() == b"bytes"
            assert request.headers["Content-Length"] == "5"
            return httpx.Response(200)
        return httpx.Response(200, stream=httpx.ByteStream(b"bytes"))

    client = AsyncStorageTransfers(
        AsyncApi(api), transport=httpx.MockTransport(handler)
    )
    assert (
        await client.upload(
            kind="trial",
            request_id="retry",
            metadata={},
            files=[UploadFile("archive", source, "archive")],
        )
    )["state"] == "completed"
    target = tmp_path / "output"
    await client.download(
        kind="trial", resource_id="id", role="archive", destination=target
    )
    assert target.read_bytes() == b"bytes"
    assert (await client.copy(kind="trial", source_id="id", overwrite=True))["complete"]
    assert [request["overwrite"] for name, request in api.calls if name == "copy"] == [
        True,
        False,
    ]


@pytest.mark.parametrize(
    "url",
    [
        "http://storage.invalid/",
        "https://user:password@storage.invalid/",
        "https://storage.invalid/#fragment",
    ],
)
def test_rejects_unsafe_transfer_urls(tmp_path, url):
    api = Api()
    api.download["url"] = url
    with pytest.raises(StorageTransferError, match="HTTPS"):
        StorageTransfers(api).download(
            kind="trial",
            resource_id="id",
            role="archive",
            destination=tmp_path / "output",
        )
    assert list(tmp_path.iterdir()) == []


class TusApi(Api):
    def __init__(self, url="https://storage.invalid/tus", chunk_size=2.0):
        super().__init__()
        self.url = url
        self.chunk_size = chunk_size

    def create_upload(self, *, request):
        session = super().create_upload(request=request)
        assert request["protocol"] == "tus"
        session["files"][0]["upload"] = {
            "protocol": "tus",
            "url": self.url,
            "headers": {"x-signature": "capability"},
            "metadata": {"objectName": "api-allocated-key"},
            "chunk_size": self.chunk_size,
        }
        return session


def tus_arguments(source):
    return {
        "kind": "task",
        "request_id": "same",
        "metadata": {},
        "files": [UploadFile("dist.tar.gz", source, "archive")],
        "protocol": "tus",
    }


def test_tus_resumes_from_server_offsets_and_preserves_session_url(
    tmp_path, monkeypatch
):
    calls = []
    uploaded = bytearray()
    fail = True
    expired = set()

    def handler(request):
        headers = request.headers
        assert headers["x-signature"] == "capability"
        assert "Authorization" not in headers
        assert headers["Tus-Resumable"] == "1.0.0"
        calls.append((request.method, str(request.url)))
        if request.method == "POST":
            assert headers["Upload-Length"] == "5"
            assert headers["Upload-Metadata"] == "objectName YXBpLWFsbG9jYXRlZC1rZXk="
            session = "/tus/fresh" if expired else "/tus/session"
            return httpx.Response(201, headers={"Location": session})
        if str(request.url) in expired:
            return httpx.Response(404)
        if request.method == "HEAD":
            return httpx.Response(200, headers={"Upload-Offset": str(len(uploaded))})
        assert request.method == "PATCH"
        assert headers["Content-Type"] == "application/offset+octet-stream"
        assert int(headers["Upload-Offset"]) == len(uploaded)
        if fail and len(uploaded) >= 2:
            raise httpx.ReadTimeout("response may contain secret signed URL")
        uploaded.extend(request.content)
        return httpx.Response(204, headers={"Upload-Offset": str(len(uploaded))})

    delays = []
    monkeypatch.setattr("harbor_client.transfers.time.sleep", delays.append)
    source = tmp_path / "archive"
    source.write_bytes(b"bytes")
    api = TusApi()
    resume_urls = {}
    client = StorageTransfers(
        api, resume_urls=resume_urls, transport=httpx.MockTransport(handler)
    )

    with pytest.raises(
        StorageTransferError, match="Resumable storage transfer failed"
    ) as failure:
        client.upload(**tus_arguments(source))
    assert "secret" not in str(failure.value)
    assert failure.value.upload_id == "upload"
    assert uploaded == b"by"
    assert delays == [1.0] * 3
    assert resume_urls == {"upload/0": "https://storage.invalid/tus/session"}
    assert [name for name, _ in api.calls] == ["prepare"]

    fail = False
    assert client.upload(**tus_arguments(source))["state"] == "completed"
    assert uploaded == b"bytes"
    assert [method for method, _ in calls].count("POST") == 1
    assert [name for name, _ in api.calls] == ["prepare", "prepare", "complete"]

    # An expired session is replaced instead of failing every later upload.
    expired.add("https://storage.invalid/tus/session")
    uploaded.clear()
    assert client.upload(**tus_arguments(source))["state"] == "completed"
    assert uploaded == b"bytes"
    assert [method for method, _ in calls].count("POST") == 2
    assert resume_urls == {"upload/0": "https://storage.invalid/tus/fresh"}


@pytest.mark.parametrize("offset", ["2", "1", "9", None])
def test_tus_rejects_stalled_or_out_of_range_offsets(tmp_path, monkeypatch, offset):
    patches = []

    def handler(request):
        if request.method == "POST":
            return httpx.Response(201, headers={"Location": "/tus/session"})
        if request.method == "HEAD":
            return httpx.Response(200, headers={"Upload-Offset": "2"})
        patches.append(request)
        if not patches[1:]:
            return httpx.Response(204, headers={"Upload-Offset": "2"})
        return httpx.Response(
            204, headers={} if offset is None else {"Upload-Offset": offset}
        )

    monkeypatch.setattr("harbor_client.transfers._TUS_RETRY_DELAY", 0.0)
    source = tmp_path / "archive"
    source.write_bytes(b"bytes")
    client = StorageTransfers(TusApi(), transport=httpx.MockTransport(handler))
    with pytest.raises(StorageTransferError, match="Resumable"):
        client.upload(**tus_arguments(source))
    assert len(patches) == 2


@contextmanager
def tus_server(behavior):
    """Serve TUS on a real loopback socket; behavior(handler) answers each request."""
    requests = []
    stop = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def handle_one_request(self):
            try:
                super().handle_one_request()
            except (BrokenPipeError, ConnectionResetError):
                self.close_connection = True

        def do_any(self):
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length)
            requests.append((self.command, self.path, body))
            behavior(self, stop)

        do_POST = do_HEAD = do_PATCH = do_any

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
    )
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", requests
    finally:
        stop.set()
        server.shutdown()
        server.server_close()


def reply(handler, status, headers=()):
    handler.send_response(status)
    for name, value in headers:
        handler.send_header(name, value)
    handler.send_header("Content-Length", "0")
    handler.end_headers()


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_tus_upload_times_out_on_a_silent_storage_server(
    tmp_path, monkeypatch, asynchronous
):
    def behavior(handler, stop):
        if handler.command == "POST":
            reply(handler, 201, [("Location", "/files/one")])
        else:
            stop.wait(10)  # Never answer the PATCH or HEAD.

    monkeypatch.setattr("harbor_client.transfers._TUS_RETRY_DELAY", 0.0)
    source = tmp_path / "archive"
    source.write_bytes(b"bytes")
    with tus_server(behavior) as (url, requests):
        api = TusApi(f"{url}/files", chunk_size=5)
        started = time.monotonic()
        with pytest.raises(StorageTransferError, match="Resumable"):
            if asynchronous:
                await AsyncStorageTransfers(AsyncApi(api), timeout=0.2).upload(
                    **tus_arguments(source)
                )
            else:
                StorageTransfers(api, timeout=0.2).upload(**tus_arguments(source))
        assert time.monotonic() - started < 5
        assert requests[0][:2] == ("POST", "/files")
        assert requests[1][0] == "PATCH"


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("redirected", ["POST", "PATCH"])
async def test_tus_does_not_follow_redirects_with_file_bytes(
    tmp_path, monkeypatch, asynchronous, redirected
):
    def elsewhere(handler, _stop):
        reply(handler, 204, [("Upload-Offset", "5"), ("Location", "/x")])

    monkeypatch.setattr("harbor_client.transfers._TUS_RETRY_DELAY", 0.0)
    source = tmp_path / "archive"
    source.write_bytes(b"bytes")
    with tus_server(elsewhere) as (other, received):

        def behavior(handler, _stop):
            if handler.command == redirected:
                reply(handler, 307, [("Location", f"{other}/stolen")])
            elif handler.command == "POST":
                reply(handler, 201, [("Location", "/files/one")])
            else:
                reply(handler, 200, [("Upload-Offset", "0")])

        with tus_server(behavior) as (url, _requests):
            api = TusApi(f"{url}/files", chunk_size=5)
            with pytest.raises(StorageTransferError):
                if asynchronous:
                    await AsyncStorageTransfers(AsyncApi(api), timeout=2).upload(
                        **tus_arguments(source)
                    )
                else:
                    StorageTransfers(api, timeout=2).upload(**tus_arguments(source))
    assert received == []


def test_generated_sdk_negotiates_transfers_without_forwarding_harbor_credentials(
    tmp_path,
):
    from harbor_client import HarborAPIClient
    from harbor_client.validation import ContractTransport

    resource_id = "00000000-0000-4000-8000-000000000001"
    upload_id = "00000000-0000-4000-8000-000000000002"
    file_id = "00000000-0000-4000-8000-000000000003"
    request_id = "00000000-0000-4000-8000-000000000004"
    receipt = {
        "id": upload_id,
        "kind": "job",
        "resource_id": resource_id,
        "state": "completed",
        "result": {"id": resource_id},
    }
    metadata = {
        "job_id": resource_id,
        "job_name": "Example",
        "config": {},
        "finished_at": "2026-11-11T00:00:00Z",
    }
    payload = b"job bytes"
    source = tmp_path / "input"
    source.write_bytes(payload)
    target = tmp_path / "output"
    calls = []

    def api_wire(request):
        import json

        assert request.headers["authorization"] == "Bearer harbor-test-token"
        assert request.headers["Harbor-API-Version"] == "2026-09-10.preview"
        route = request.url.path.removeprefix("/functions/v1/api")
        calls.append(route)
        body = json.loads(request.read()) if request.content else {}
        if route == "/v1/storage/uploads":
            assert body["request_id"] == request_id
            assert body["metadata"] == metadata
            expected = body["files"][0]
            assert expected["sha256"] == hashlib.sha256(payload).hexdigest()
            return httpx.Response(
                200,
                json={
                    **receipt,
                    "state": "pending",
                    "result": None,
                    "expires_at": "2099-01-01T00:00:00Z",
                    "files": [{**expected, "id": file_id, "upload": grant("PUT")}],
                },
            )
        if route == f"/v1/storage/uploads/{upload_id}/complete":
            assert not body
            return httpx.Response(200, json=receipt)
        if route == f"/v1/jobs/{resource_id}/artifacts":
            assert request.url.params["artifact_type"] == "archive"
            assert not body
            return httpx.Response(
                200, json=grant(size_bytes=len(payload), version="object-version")
            )
        assert route == f"/v1/jobs/{resource_id}/copy"
        assert body == {}
        return httpx.Response(
            200,
            json={
                "job_id": file_id,
                "job_name": "Copied example",
                "already_existed": False,
                "overwritten": False,
                "n_trials": 0,
                "n_trials_skipped": 0,
                "n_objects_total": 1,
                "n_objects_done": 0,
                "n_objects": 1,
                "n_copied": 1,
                "n_already_copied": 0,
                "n_failed": 0,
                "n_remaining": 0,
                "complete": True,
            },
        )

    def storage_wire(request):
        safe_headers(request)
        calls.append(request.method)
        if request.method == "PUT":
            assert request.read() == payload
            return httpx.Response(200)
        return httpx.Response(200, stream=httpx.ByteStream(payload))

    with httpx.Client(
        transport=ContractTransport(httpx.MockTransport(api_wire))
    ) as http:
        client = HarborAPIClient(
            harbor_api_version="2026-09-10.preview",
            token="harbor-test-token",
            httpx_client=http,
        )
        client.transfers.transport = httpx.MockTransport(storage_wire)
        result = client.transfers.upload(
            kind="job",
            request_id=request_id,
            metadata=metadata,
            files=[UploadFile("job.tar.gz", source, "archive")],
        )
        assert result.state == "completed"
        client.transfers.download(
            kind="job", resource_id=resource_id, role="archive", destination=target
        )
        assert target.read_bytes() == payload
        assert client.transfers.copy(kind="job", source_id=resource_id).complete
    assert calls == [
        "/v1/storage/uploads",
        "PUT",
        f"/v1/storage/uploads/{upload_id}/complete",
        f"/v1/jobs/{resource_id}/artifacts",
        "GET",
        f"/v1/jobs/{resource_id}/copy",
    ]


def test_retry_upload_only_transfers_missing_files_then_verifies_entire_session(
    tmp_path,
):
    uploaded = set()
    seen = []
    interrupted = True

    class ResumeApi(Api):
        def create_upload(self, *, request):
            session = super().create_upload(request=request)
            session["files"] = [
                file for file in session["files"] if file["path"] not in uploaded
            ]
            for file in session["files"]:
                file["upload"]["url"] = (
                    f"https://storage.invalid/{file['path']}?token=secret"
                )
            return session

    def handler(request):
        name = request.url.path.lstrip("/")
        seen.append(name)
        if interrupted and name == "second":
            return httpx.Response(503)
        uploaded.add(name)
        return httpx.Response(200)

    files = []
    for name in ("first", "second"):
        source = tmp_path / name
        source.write_bytes(name.encode())
        files.append(UploadFile(name, source))
    api = ResumeApi()
    helper = StorageTransfers(api, transport=httpx.MockTransport(handler))
    arguments = {
        "kind": "dataset",
        "request_id": "same",
        "metadata": {},
        "files": files,
    }
    with pytest.raises(StorageTransferError):
        helper.upload(**arguments)
    assert [name for name, _ in api.calls] == ["prepare"]
    assert uploaded == {"first"}

    interrupted = False
    assert helper.upload(**arguments)["state"] == "completed"
    assert seen == ["first", "second", "second"]
    assert uploaded == {"first", "second"}
    # An empty set of missing descriptors still requires server verification.
    assert helper.upload(**arguments)["state"] == "completed"
    assert seen == ["first", "second", "second"]
    assert [name for name, _ in api.calls] == [
        "prepare",
        "prepare",
        "complete",
        "prepare",
        "complete",
    ]
