## 1.0.0 - 2026-11-12
* feat!: remove context-manager support, transfers client, and tighten response types
* This release removes several public APIs and tightens a number of
* response-model field types, making previously-Optional fields required.
* Callers that relied on context-manager usage (`with`/`async with`),
* the `transfers` property, or that handled `None` for the affected
* fields must update their code.
* Key changes:
* Remove `close()`, `__enter__`/`__exit__`, `aclose()`, `__aenter__`/`__aexit__` from both `HarborAPIClient` and `AsyncHarborAPIClient`
* Remove `transfers` property (and `StorageTransfers` / `AsyncStorageTransfers`) from both client classes
* Tighten Optional → required on `created_by_user`, `owner_organization`, `cancellation`, `manual_pause`, `stats`, `circuit`, `paused_by_user`, `requested_by_user`, `package`, and `job_created_by_user` across multiple response models
* Fix async pagination to use a simple `for` loop instead of `to_async(next)`, and add early-exit on empty pages
* Widen `storage_path` from `None` to `Optional[Any]` and `step_results` from `None` to `Optional[Any]`
* Drop `tus` optional dependency and `jsonschema` dependency; lower Python requirement from 3.12 to 3.9
* Rename package from `harbor-client` to `harbor-framework-client`
* 🌿 Generated with Fern

