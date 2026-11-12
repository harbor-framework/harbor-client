## 1.0.0 - 2026-11-12
* feat!: remove context-manager support, transfers property, and tighten response field types
* This release removes several public APIs and tightens type contracts across
* multiple response models, constituting a breaking change for existing callers.
* Key changes:
* Remove `close()`/`__enter__`/`__exit__` and `aclose()`/`__aenter__`/`__aexit__` from `HarborAPIClient` and `AsyncHarborAPIClient`, dropping context-manager support
* Remove the `transfers` property (and `StorageTransfers`/`AsyncStorageTransfers`) from both client classes
* Tighten previously-Optional response fields to required (non-Optional) on `JobSummary`, `JobDetail`, `JobOverview`, `JobTrialSummary`, `JobCancellationSummary`, `TrialDetail`, `PackagePublicGrant`, `RegistryPackageVersionPage`, and `EvaluationSummaryRow`
* Change `timeout_in_seconds` in `RequestOptions` from `float` to `int`
* Fix async pagination to use a simple `for` loop instead of `to_async(next)`, and add early-exit on empty pages
* Broaden `StoragePublicationFile.storage_path` from `None` to `Optional[Any]` and `TrialDetail.step_results` from `None` to `Optional[Any]`
* Lower minimum Python version requirement from 3.12 to 3.9
* 🌿 Generated with Fern

