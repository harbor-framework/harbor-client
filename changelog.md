## 1.0.0 - 2026-11-12
* feat!: remove context-manager support, transfers client, and tighten response field types
* This release removes several public APIs and tightens a number of
* response model field types, all of which constitute breaking changes for
* existing callers.
* Key changes:
* Remove `close()`/`__enter__`/`__exit__` and `aclose()`/`__aenter__`/`__aexit__` from `HarborAPIClient` and `AsyncHarborAPIClient`, ending context-manager support
* Remove the `transfers` property (and `StorageTransfers`/`AsyncStorageTransfers`) from both client classes
* Promote previously-`Optional` fields to required (non-`Optional`) across `JobDetail`, `JobOverview`, `JobSummary`, `JobTrialSummary`, `JobCancellationSummary`, `TrialDetail`, `PackagePublicGrant`, and `RegistryPackageVersionPage`
* Remove `_reject_unsupported_property` field validator from `HostedAgentConfig`, allowing `secret_bindings` and `secret_tags` to be set
* Change `timeout_in_seconds` in `RequestOptions` from `float` to `int`
* Widen `StoragePublicationFile.storage_path` from `None` to `Optional[Any]` and `TrialDetail.step_results` from `None` to `Optional[Any]`
* Fix pagination across all async pagers to use a simple `for` loop instead of `to_async(next)`, and add early-exit on empty pages
* Lower minimum Python version requirement from 3.12 to 3.9
* 🌿 Generated with Fern

