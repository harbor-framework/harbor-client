## 1.0.0 - 2026-11-13
### Breaking Changes
* **`HarborAPIClient`** and **`AsyncHarborAPIClient`** — context-manager support (`close()` / `aclose()`, `__enter__` / `__exit__`, `__aenter__` / `__aexit__`) removed; callers must manage HTTP session lifecycle manually.
* **`HarborAPIClient.transfers`** / **`AsyncHarborAPIClient.transfers`** — properties removed; the `StorageTransfers` / `AsyncStorageTransfers` workflow is no longer accessible via the client.
* **`JobsClient.submit()`** — required `relay_inference` parameter removed and return type changed from `SubmitJobResponse` to `JobSubmission`; remove `relay_inference=` from all call sites and update type annotations to `JobSubmission`.
* **`JobsClient.get()`**, **`JobsClient.cancel()`**, and **`PackagesClient.list_version_catalog()`** — `get()` now returns `ResultJob` instead of `JobDetail`; `cancel()` drops required `soft` parameter in favour of optional `finish_running`; `list_version_catalog()` renames keyword argument `organization_name` → `organization_id`; update call sites accordingly.
* **Multiple public model types removed** — `CancelJobWithIdRequest` (renamed to `CancelHostedJobRequest`), `SubmitJobResponse`, `JobDetail`, `CancelAllJobTrialsRequest`, `RetryTrialsByFilterRequest`, and related trial/artifact/verifier types are no longer exported; remove all references and migrate to replacement types where available.
### Added
* **`job_credentials`** — optional parameter added to `JobsClient.submit()` for supplying job-level credentials at submission time.
### Fixed
* **Pagination** — all clients now correctly stop iteration when an empty page is returned, preventing infinite loops on exhausted result sets.

