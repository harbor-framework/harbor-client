# Harbor API Python SDK

Typed synchronous and asynchronous clients for the [Harbor](https://harborframework.com) API.

```sh
pip install harbor-framework-client
```

The distribution is named `harbor-framework-client` and the import package is `harbor_client`. The unrelated `harbor-client` project on PyPI is a different package. Python 3.12 or newer is required. Install the `tus` extra for resumable uploads: `pip install "harbor-framework-client[tus]"`.

## Quickstart

```python
from harbor_client import HarborAPIClient

with HarborAPIClient(token="your-api-key") as client:
    for job in client.jobs.list(state="running"):
        print(job.id, job.name)
```

`token` takes a string or a callable that returns the current token. Each client owns one connection pool; use it as a context manager or call `close()`.

### Async

```python
import asyncio

from harbor_client import AsyncHarborAPIClient


async def main() -> None:
    async with AsyncHarborAPIClient(token="your-api-key") as client:
        async for job in client.jobs.list():
            print(job.id, job.name)


asyncio.run(main())
```

`AsyncHarborAPIClient` also accepts `async_token`, an async callable that returns the token. Call `await client.aclose()` when you do not use the context manager.

## Pagination

List methods return pagers. Iterate a pager for items across all pages, or use `iter_pages()` for one page at a time:

```python
pager = client.jobs.list(page_size="50")
for page in pager.iter_pages():
    print(len(page))
```

## Errors

HTTP errors raise `harbor_client.core.ApiError` or one of its subclasses exported from `harbor_client`, such as `NotFoundError`, `UnauthorizedError` and `ConflictError`. The error carries `status_code` and the parsed problem `body`; its message shows the problem's `detail`. Error messages never include request or response headers.

```python
from harbor_client import NotFoundError

try:
    client.jobs.get(job_id="3f6c2a1e-8b4d-4e2a-9c1f-5d7e8a9b0c12")
except NotFoundError as error:
    print(error.status_code, error.body)
```

The client validates requests and responses against the API contract it was built from. A request or response that does not match raises `harbor_client.ContractError`.

## Configuration

| Option | Purpose |
| --- | --- |
| `base_url` | Target another deployment. `client.set_base_url(...)` changes it later. |
| `harbor_api_version` | API version sent in the `Harbor-API-Version` header. Defaults to the version this release was generated from. |
| `timeout`, `retry` | Default request timeout in seconds and retry policy. |
| `headers` | Extra headers sent with every request. |
| `transport` | A custom `httpx.BaseTransport`, for example for proxies or tests. |
| `httpx_client`, `http_client` | Reuse an `httpx.Client` or a `requests.Session`. An `httpx.AsyncClient` is not accepted. |

Per call, pass `request_options={"timeout_in_seconds": 30, "max_retries": 2}`, or `additional_headers` and `additional_query_parameters`.

## File transfers

`StorageTransfers` uploads and downloads task, dataset, job and trial files through signed storage grants, including resumable TUS uploads:

```python
from pathlib import Path

from harbor_client import UploadFile
from harbor_client.transfers import StorageTransfers

transfers = StorageTransfers(client)
transfers.download(
    kind="job",
    resource_id="3f6c2a1e-8b4d-4e2a-9c1f-5d7e8a9b0c12",
    role="archive",
    destination=Path("job.tar.gz"),
)
```

Use `AsyncStorageTransfers` with `AsyncHarborAPIClient`. Upload sources must stay unchanged until the upload completes. A failed transfer raises `StorageTransferError`, which carries `upload_id` so `complete_upload` can resume a finished upload.

## Reference

[reference.md](https://github.com/harbor-framework/harbor-client/blob/main/reference.md) lists every resource and method.

## License

Apache-2.0. See [LICENSE](https://github.com/harbor-framework/harbor-client/blob/main/LICENSE).
