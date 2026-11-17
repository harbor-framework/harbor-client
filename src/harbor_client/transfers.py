"""Storage workflows over generated Harbor calls and isolated signed HTTP transfers.

No storage provider SDK or application credentials are used for byte transfers.
HTTP uploads are not automatically retried: replaying a completed PUT can conflict.
Use the same request ID and ``complete_upload`` to recover a lost completion reply.
TUS upload URLs can be retained in a caller-owned mapping to resume interrupted files.
"""

from __future__ import annotations

import asyncio
from base64 import b64encode
from collections.abc import Callable, Generator, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
import hashlib
from pathlib import Path
import tempfile
import tarfile
import shutil
import time
from typing import Any, Literal
from urllib.parse import urljoin, urlsplit

import httpx

Kind = Literal["task", "dataset", "job", "trial"]
Role = Literal["archive", "file", "trajectory", "log"]


class StorageTransferError(RuntimeError):
    """Sanitized transfer failure, retaining identities needed for recovery."""

    def __init__(
        self,
        message: str,
        *,
        upload_id: str | None = None,
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.upload_id = upload_id
        self.status_code = status_code


@dataclass(frozen=True)
class UploadFile:
    """One local file and its logical path, never its storage bucket or key."""

    path: str
    source: Path
    role: Role = "file"
    optional: bool = False

    def descriptor(self) -> dict[str, Any]:
        digest = hashlib.sha256()
        size = 0
        with Path(self.source).open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
                size += len(chunk)
        descriptor = {
            "path": self.path,
            "role": self.role,
            "size_bytes": size,
            "sha256": digest.hexdigest(),
        }
        if self.optional:
            descriptor["optional"] = True
        return descriptor


def _value(value: Any, key: str) -> Any:
    return value[key] if isinstance(value, Mapping) else getattr(value, key)


def _request(grant: Any, method: str, *, content: Any = None) -> httpx.Request:
    if _value(grant, "protocol") != "http" or _value(grant, "method") != method:
        raise StorageTransferError("Unsupported storage transfer protocol or method")
    url = _value(grant, "url")
    parsed = urlsplit(url)
    if (
        (
            parsed.scheme != "https"
            and not (
                parsed.scheme == "http"
                and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
            )
        )
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise StorageTransferError(
            "Storage transfer URL must use HTTPS (HTTP is allowed for loopback development)"
        )
    # Construct Request directly: Client.build_request/request merge default headers
    # and cookies, potentially attaching the Harbor credential to another origin.
    return httpx.Request(
        method, url, headers=dict(_value(grant, "headers")), content=content
    )


def _check(response: httpx.Response, upload_id: str | None = None) -> None:
    if not response.is_success:
        raise StorageTransferError(
            "Storage transfer failed",
            status_code=response.status_code,
            upload_id=upload_id,
        )


def _files(
    files: Sequence[UploadFile],
) -> tuple[dict[str, UploadFile], list[dict[str, Any]]]:
    by_path = {file.path: file for file in files}
    if len(by_path) != len(files):
        raise ValueError("Upload file paths must be unique")
    return by_path, [file.descriptor() for file in files]


def _download_grant(
    client: Any,
    kind: Kind,
    resource_id: str,
    role: Role,
    path: str | None,
    transfer_id: str | None,
    dataset_version_id: str | None,
) -> Any:
    if kind in {"task", "dataset"}:
        query = {"version_id": resource_id}
        if transfer_id is not None:
            query["transfer_id"] = transfer_id
        if role == "file" and path:
            if dataset_version_id is not None:
                raise ValueError("Dataset attribution applies to task archives")
            return client.packages.download_file(file=path, **query)
        if kind == "task" and role == "archive" and path is None:
            if dataset_version_id is not None:
                query["dataset_version_id"] = dataset_version_id
            return client.packages.download_archive(**query)
        raise ValueError("Package download requires an archive or a logical file path")
    if path is not None or transfer_id is not None or dataset_version_id is not None:
        raise ValueError("Package paths and attribution apply to package downloads")
    if kind == "job" and role in {"archive", "log"}:
        return client.jobs.get_artifact_download(job_id=resource_id, artifact_type=role)
    if kind == "trial" and role in {"archive", "trajectory"}:
        return client.trials.get_artifact_download(
            trial_id=resource_id, artifact_type=role
        )
    raise ValueError("Invalid artifact kind or role")


def _copy_pass(
    client: Any, kind: str, source_id: str, options: Mapping[str, Any]
) -> Any:
    if kind == "job":
        return client.jobs.copy(source_job_id=source_id, **options)
    if kind == "trial":
        return client.trials.copy(source_trial_id=source_id, **options)
    raise ValueError("Only jobs and trials can be copied")


def _copy_summary(result: Any, copied: int) -> Any:
    if isinstance(result, Mapping):
        return {**result, "n_copied": copied}
    return result.model_copy(update={"n_copied": copied})


def _expected(session: Any, by_path: Mapping[str, UploadFile]) -> list[Any]:
    expected = list(_value(session, "files"))
    paths = [_value(file, "path") for file in expected]
    if len(set(paths)) != len(paths) or not set(paths).issubset(by_path):
        raise StorageTransferError(
            "Upload session returned an unexpected file manifest",
            upload_id=_value(session, "id"),
        )
    return expected


def _check_size(actual: int, grant: Any) -> None:
    expected = _value(grant, "size_bytes")
    if expected is not None and actual != expected:
        raise StorageTransferError(
            "Downloaded file size did not match artifact metadata"
        )


def _temporary(destination: Path) -> Path:
    # Write alongside the destination so replacement is atomic, and never leave a
    # truncated artifact at the user's requested path after an interrupted GET.
    with tempfile.NamedTemporaryFile(
        prefix=".harbor-transfer-", dir=destination.parent, delete=False
    ) as stream:
        return Path(stream.name)


def _finish_download(temporary: Path, target: Path, grant: Any) -> None:
    member = (
        grant.get("archive_member")
        if isinstance(grant, Mapping)
        else getattr(grant, "archive_member", None)
    )
    if not member:
        temporary.replace(target)
        return
    extracted = _temporary(target)
    found = False
    try:
        # Read only the requested regular member; never extract filesystem paths
        # or follow links from a user-authored archive.
        with tarfile.open(temporary, mode="r|*") as archive:
            for entry in archive:
                if entry.name != member:
                    continue
                if found or not entry.isfile():
                    raise StorageTransferError(
                        "Archive member is ambiguous or is not a regular file"
                    )
                source = archive.extractfile(entry)
                if source is None:
                    raise StorageTransferError("Archive member is unavailable")
                with source, extracted.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
                found = True
        if not found:
            raise StorageTransferError(
                "Requested file is absent from the package archive"
            )
        extracted.replace(target)
    except (tarfile.TarError, EOFError):
        raise StorageTransferError("Package archive is invalid") from None
    finally:
        extracted.unlink(missing_ok=True)


_TUS_RETRIES = 3
_TUS_RETRY_DELAY = 1.0
# Sends back the response to each request, or None after a retry delay.
_TusStep = Generator[httpx.Request | float, Any, None]


class _TusDone(Exception):
    """The storage already holds these bytes (409); completion verifies them."""


def _tus_offset(response: httpx.Response, current: int, size: int) -> int:
    if response.status_code == 409:
        raise _TusDone
    try:
        offset = int(response.headers["Upload-Offset"])
    except (KeyError, ValueError):
        offset = -1
    # A stalled or out-of-range offset would otherwise repeat the same request forever.
    if not response.is_success or not current <= offset <= size:
        raise StorageTransferError("Resumable storage transfer failed")
    return offset


def _tus_steps(
    grant: Any, source: Path, key: str, resume_urls: MutableMapping[str, str]
) -> _TusStep:
    """Yield TUS 1.0 requests (or retry delays) over the SDK's isolated HTTP client."""
    url = _value(grant, "url")
    # Apply the same endpoint validation as HTTP without interpreting metadata.
    _request({"protocol": "http", "method": "PUT", "url": url, "headers": {}}, "PUT")
    chunk_size = _value(grant, "chunk_size")
    # Fern may decode JSON numbers as floats. TUS needs a whole byte count.
    if (
        not isinstance(chunk_size, (int, float))
        or chunk_size <= 0
        or chunk_size % 1 != 0
    ):
        raise StorageTransferError("Invalid resumable upload chunk size")

    def same_origin(location: str) -> str:
        if urlsplit(location)[:2] != urlsplit(url)[:2]:
            raise StorageTransferError(
                "Resumable upload URL belongs to another storage origin"
            )
        return location

    headers = {**dict(_value(grant, "headers")), "Tus-Resumable": "1.0.0"}
    size = source.stat().st_size
    resume = resume_urls.get(key)
    offset = 0
    if resume:
        same_origin(resume)
        response = yield httpx.Request("HEAD", resume, headers=headers)
        if response.status_code in {404, 410}:
            resume = None  # The session expired; start a new one.
        else:
            offset = _tus_offset(response, 0, size)
    if not resume:
        metadata = ",".join(
            f"{name} {b64encode(str(value).encode()).decode('ascii')}"
            for name, value in dict(_value(grant, "metadata")).items()
        )
        response = yield httpx.Request(
            "POST",
            url,
            headers={
                **headers,
                "Upload-Length": str(size),
                "Upload-Metadata": metadata,
            },
        )
        if response.status_code == 409:
            raise _TusDone
        location = response.headers.get("Location")
        if not response.is_success or location is None:
            raise StorageTransferError("Resumable storage transfer failed")
        resume = same_origin(urljoin(url, location))
        resume_urls[key] = resume
    retries = 0
    with source.open("rb") as stream:
        while offset < size:
            stream.seek(offset)
            try:
                response = yield httpx.Request(
                    "PATCH",
                    resume,
                    headers={
                        **headers,
                        "Content-Type": "application/offset+octet-stream",
                        "Upload-Offset": str(offset),
                    },
                    content=stream.read(int(chunk_size)),
                )
            except httpx.TransportError:
                response = None
            if response is not None and (
                response.is_success or response.status_code == 409
            ):
                offset = _tus_offset(response, offset + 1, size)
                retries = 0
                continue
            if retries == _TUS_RETRIES:
                raise StorageTransferError("Resumable storage transfer failed")
            retries += 1
            yield _TUS_RETRY_DELAY
            response = yield httpx.Request("HEAD", resume, headers=headers)
            offset = _tus_offset(response, 0, size)


def _tus_upload(
    http: httpx.Client,
    grant: Any,
    source: Path,
    key: str,
    resume_urls: MutableMapping[str, str],
) -> None:
    steps = _tus_steps(grant, source, key, resume_urls)
    try:
        step = next(steps)
        while True:
            if isinstance(step, float):
                time.sleep(step)
                step = steps.send(None)
                continue
            try:
                response = http.send(step, auth=None)
            except httpx.TransportError as error:
                step = steps.throw(error)
            else:
                step = steps.send(response)
    except (StopIteration, _TusDone):
        return
    except StorageTransferError:
        raise
    except Exception:
        # Transport diagnostics may contain signed URLs or metadata.
        raise StorageTransferError("Resumable storage transfer failed") from None


async def _async_tus_upload(
    http: httpx.AsyncClient,
    grant: Any,
    source: Path,
    key: str,
    resume_urls: MutableMapping[str, str],
) -> None:
    steps = _tus_steps(grant, source, key, resume_urls)
    try:
        step = next(steps)
        while True:
            if isinstance(step, float):
                await asyncio.sleep(step)
                step = steps.send(None)
                continue
            try:
                response = await http.send(step, auth=None)
            except httpx.TransportError as error:
                step = steps.throw(error)
            else:
                step = steps.send(response)
    except (StopIteration, _TusDone):
        return
    except StorageTransferError:
        raise
    except Exception:
        raise StorageTransferError("Resumable storage transfer failed") from None


class StorageTransfers:
    """Workflows over generated storage, package, job, and trial methods."""

    def __init__(
        self,
        client: Any,
        *,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 60,
        resume_urls: MutableMapping[str, str] | None = None,
    ):
        self.client = client
        self.transport = transport
        self.timeout = timeout
        self.resume_urls = resume_urls if resume_urls is not None else {}

    def upload(
        self,
        *,
        kind: Kind,
        request_id: str,
        metadata: Mapping[str, Any],
        files: Sequence[UploadFile],
        protocol: Literal["http", "tus"] = "http",
        **resource: Any,
    ) -> Any:
        by_path, descriptors = _files(files)
        session = self.client.storage.create_upload(
            request={
                "kind": kind,
                "request_id": request_id,
                "metadata": dict(metadata),
                "files": descriptors,
                "protocol": protocol,
                **resource,
            },
        )
        upload_id = _value(session, "id")
        if _value(session, "state") in {"verified", "completed"}:
            return self.complete_upload(upload_id)
        expected = _expected(session, by_path)
        try:
            with httpx.Client(
                transport=self.transport, timeout=self.timeout, follow_redirects=False
            ) as http:
                for file in expected:
                    try:
                        source = Path(by_path[_value(file, "path")].source)
                        if source.stat().st_size != _value(file, "size_bytes"):
                            raise StorageTransferError(
                                "Upload source changed after preparation",
                                upload_id=upload_id,
                            )
                        grant = _value(file, "upload")
                        if _value(grant, "protocol") == "tus":
                            _tus_upload(
                                http,
                                grant,
                                source,
                                f"{upload_id}/{_value(file, 'id')}",
                                self.resume_urls,
                            )
                        else:
                            with source.open("rb") as stream:
                                response = http.send(
                                    _request(grant, "PUT", content=stream),
                                    auth=None,
                                    stream=True,
                                )
                                try:
                                    if response.status_code != 409:
                                        _check(response, upload_id)
                                finally:
                                    response.close()
                    except (StorageTransferError, httpx.HTTPError, OSError):
                        if not by_path[_value(file, "path")].optional:
                            raise
        except StorageTransferError as error:
            if error.upload_id is None:
                error.upload_id = upload_id
            raise
        except (httpx.HTTPError, OSError):
            raise StorageTransferError(
                "Storage upload interrupted", upload_id=upload_id
            ) from None
        return self.complete_upload(upload_id)

    def complete_upload(self, upload_id: str) -> Any:
        """Verify and publish, including recovery after a lost completion reply."""
        return self.client.storage.complete_upload(upload_id=upload_id)

    def download(
        self,
        *,
        kind: Kind,
        resource_id: str,
        role: Role,
        destination: Path,
        path: str | None = None,
        transfer_id: str | None = None,
        dataset_version_id: str | None = None,
    ) -> Path:
        grant = _download_grant(
            self.client, kind, resource_id, role, path, transfer_id, dataset_version_id
        )
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = _temporary(target)
        try:
            with httpx.Client(
                transport=self.transport, timeout=self.timeout, follow_redirects=False
            ) as http:
                response = http.send(_request(grant, "GET"), auth=None, stream=True)
                try:
                    _check(response)
                    count = 0
                    with temporary.open("wb") as stream:
                        for chunk in response.iter_raw():
                            stream.write(chunk)
                            count += len(chunk)
                    _check_size(count, grant)
                finally:
                    response.close()
            _finish_download(temporary, target, grant)
        except StorageTransferError:
            raise
        except (httpx.HTTPError, OSError):
            raise StorageTransferError("Storage download interrupted") from None
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def copy(
        self,
        *,
        kind: Literal["job", "trial"],
        source_id: str,
        max_passes: int = 50,
        on_round: Callable[[Any], None] | None = None,
        **options: Any,
    ) -> Any:
        """Drive existing resumable copy passes; stopping the SDK stops new passes."""
        if max_passes < 1:
            raise ValueError("max_passes must be positive")
        copied = 0
        for _ in range(max_passes):
            result = _copy_pass(self.client, kind, source_id, options)
            copied += _value(result, "n_copied")
            if on_round is not None:
                on_round(result)
            if _value(result, "complete") or _value(result, "n_copied") == 0:
                return _copy_summary(result, copied)
            # Overwrite recaptures database metadata. It belongs only on pass one.
            options = {**options, "overwrite": False}
        return _copy_summary(result, copied)


class AsyncStorageTransfers:
    """Async workflows over the same isolated, redirect-free signed transfers."""

    def __init__(
        self,
        client: Any,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout: float = 60,
        resume_urls: MutableMapping[str, str] | None = None,
    ):
        self.client = client
        self.transport = transport
        self.timeout = timeout
        self.resume_urls = resume_urls if resume_urls is not None else {}

    async def upload(
        self,
        *,
        kind: Kind,
        request_id: str,
        metadata: Mapping[str, Any],
        files: Sequence[UploadFile],
        protocol: Literal["http", "tus"] = "http",
        **resource: Any,
    ) -> Any:
        by_path, descriptors = await asyncio.to_thread(_files, files)
        session = await self.client.storage.create_upload(
            request={
                "kind": kind,
                "request_id": request_id,
                "metadata": dict(metadata),
                "files": descriptors,
                "protocol": protocol,
                **resource,
            },
        )
        upload_id = _value(session, "id")
        if _value(session, "state") in {"verified", "completed"}:
            return await self.complete_upload(upload_id)
        expected = _expected(session, by_path)
        try:
            async with httpx.AsyncClient(
                transport=self.transport, timeout=self.timeout, follow_redirects=False
            ) as http:
                for file in expected:
                    try:
                        source = Path(by_path[_value(file, "path")].source)
                        if source.stat().st_size != _value(file, "size_bytes"):
                            raise StorageTransferError(
                                "Upload source changed after preparation",
                                upload_id=upload_id,
                            )
                        grant = _value(file, "upload")
                        if _value(grant, "protocol") == "tus":
                            await _async_tus_upload(
                                http,
                                grant,
                                source,
                                f"{upload_id}/{_value(file, 'id')}",
                                self.resume_urls,
                            )
                        else:

                            async def chunks(file_path: Path = source):
                                with file_path.open("rb") as stream:
                                    while chunk := await asyncio.to_thread(
                                        stream.read, 1024 * 1024
                                    ):
                                        yield chunk

                            request = _request(grant, "PUT", content=chunks())
                            request.headers["Content-Length"] = str(
                                _value(file, "size_bytes")
                            )
                            request.headers.pop("Transfer-Encoding", None)
                            response = await http.send(request, auth=None, stream=True)
                            try:
                                if response.status_code != 409:
                                    _check(response, upload_id)
                            finally:
                                await response.aclose()
                    except (StorageTransferError, httpx.HTTPError, OSError):
                        if not by_path[_value(file, "path")].optional:
                            raise
        except StorageTransferError as error:
            if error.upload_id is None:
                error.upload_id = upload_id
            raise
        except (httpx.HTTPError, OSError):
            raise StorageTransferError(
                "Storage upload interrupted", upload_id=upload_id
            ) from None
        return await self.complete_upload(upload_id)

    async def complete_upload(self, upload_id: str) -> Any:
        return await self.client.storage.complete_upload(upload_id=upload_id)

    async def download(
        self,
        *,
        kind: Kind,
        resource_id: str,
        role: Role,
        destination: Path,
        path: str | None = None,
        transfer_id: str | None = None,
        dataset_version_id: str | None = None,
    ) -> Path:
        grant = await _download_grant(
            self.client, kind, resource_id, role, path, transfer_id, dataset_version_id
        )
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = _temporary(target)
        try:
            async with httpx.AsyncClient(
                transport=self.transport, timeout=self.timeout, follow_redirects=False
            ) as http:
                response = await http.send(
                    _request(grant, "GET"), auth=None, stream=True
                )
                try:
                    _check(response)
                    count = 0
                    with temporary.open("wb") as stream:
                        async for chunk in response.aiter_raw():
                            await asyncio.to_thread(stream.write, chunk)
                            count += len(chunk)
                    _check_size(count, grant)
                finally:
                    await response.aclose()
            _finish_download(temporary, target, grant)
        except StorageTransferError:
            raise
        except (httpx.HTTPError, OSError):
            raise StorageTransferError("Storage download interrupted") from None
        finally:
            temporary.unlink(missing_ok=True)
        return target

    async def copy(
        self,
        *,
        kind: Literal["job", "trial"],
        source_id: str,
        max_passes: int = 50,
        on_round: Callable[[Any], None] | None = None,
        **options: Any,
    ) -> Any:
        if max_passes < 1:
            raise ValueError("max_passes must be positive")
        copied = 0
        for _ in range(max_passes):
            result = await _copy_pass(self.client, kind, source_id, options)
            copied += _value(result, "n_copied")
            if on_round is not None:
                on_round(result)
            if _value(result, "complete") or _value(result, "n_copied") == 0:
                return _copy_summary(result, copied)
            options = {**options, "overwrite": False}
            await asyncio.sleep(0)
        return _copy_summary(result, copied)
