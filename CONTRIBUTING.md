# Maintaining the Harbor API Python SDK

This repository is generated with [Fern](https://buildwithfern.com) from the Harbor API's OpenAPI document. User documentation is in [README.md](README.md); this file covers regeneration, custom code and releases.

## Regeneration

The API implementation owns the public OpenAPI document. This repository keeps its input snapshot and Fern configuration. To regenerate after the API's checked-in OpenAPI documents change, run the Generate SDK workflow manually. It also accepts `spec_ref=hub-openapi` for an automated trigger that pushes the document to this repository's `hub-openapi` branch; no such trigger is configured yet. A push to `main` that changes Fern configuration or the workflow regenerates from the committed `fern/openapi.json`; merging a regeneration PR, which only updates that document, does not start another. Fern opens SDK update pull requests against this repository. It owns generation commits, customization detection, three-way merging, and `.fern/replay.lock`. Review the generated changes and CI results before merging.

For an unmerged API candidate, commit its OpenAPI document to `fern/openapi.json` on an SDK preview branch and run the workflow with `spec_ref` set to that branch. Alternatively supply `spec_url` for an HTTPS document. `sdk_branch` selects the base branch for Fern's update PR; it defaults to `main`. The workflow uses the same pinned SDK profile and attaches the exact selected contract. Checked-client API version defaults follow that contract automatically. No API deployment is needed. Whitespace or object-key ordering changes alone do not trigger regeneration. Without either input, the workflow reads the deployed document, which the `OPENAPI_SPEC_URL` repository variable can change.

Regeneration stays at SDK version `0.1.0` during preview development. Runs without an override pass that version explicitly to Fern. When we choose a new version, `sdk_version` uses Fern's version flag to update all generated version metadata together. Review the generated changelog before merging: the pinned publisher can describe preserved Replay customizations as removals. No custom versioning engine is used.

Commit necessary edits to generated files normally: Fern Replay detects them on the next regeneration. Resolve conflicts with `npx fern-replay resolve .`; do not edit the lockfile by hand or accept unresolved patches. SDK checks on a pull request fail when a Replay patch is unresolved, when a patch on the base branch is missing from the pull request, or when Fern skipped Replay for a generation. `.fernignore` protects the fully owned validation/transfer helpers, packaging support, tests, and CI. It does not freeze generated resource clients or models.

The SDK retains regression tests for all documented operations, pagination, wire validation, pooling, and signed transfers. Static export stubs are derived from Fern's model registry during the standard package build; there is no separate SDK assembly or patch-generation command.

## Releases

Generation and release are separate. After an SDK update is reviewed and merged, publish a GitHub release tagged `v<package version>` to run the release workflow. It requires SDK checks, builds distributions and publishes with PyPI trusted publishing. Starting the workflow manually runs verification and builds only; it never publishes. Build files and authenticated generation logs are not uploaded as Actions artifacts.

One-time PyPI setup: register `harbor-framework/harbor-client`, workflow `release.yml`, and environment `pypi` as the trusted publisher for `harbor-framework-client`. No PyPI API token is needed. Configure GitHub's `pypi` environment to restrict release deployments to the intended tags.

Fern 6.17.0's SDK Config publishing preview emitted compile/test jobs but no publish job. The release workflow therefore uses the official PyPA action, following [Fern's documented publishing fallback](https://buildwithfern.com/learn/sdks/generators/python/publishing#path-2-manual-ci-workflow-update). Generation and Replay still use Fern's native publisher.

## Ownership of custom code

Fern owns generated resource clients, models, imports and formatting. Project lint and formatting checks cover tests, packaging support and the handwritten public client and helper modules; they do not rewrite generated source.

The remaining customizations have behavioral regression tests:

- `validation.py` enforces JSON Schema constraints the generator does not preserve.
- `transfers.py` orchestrates signed byte transfers and resumable uploads over generated endpoint methods.
- Replay preserves pagination, URL encoding, connection lifetime and model-fidelity fixes until the generator provides them.
- `setup.py` derives static export stubs during package builds. Packaging metadata includes these stubs and the validation contract.

Avoid cosmetic edits to generated files. When an upstream fix replaces a customization, verify its regression tests and retire the obsolete patch through Fern's Replay tools.

## Fern configuration support

Packaging requirements and user documentation are declared in `fern/sdk-config.yml`. Python generator 6.17.0 currently ignores `pythonVersion`, `extras`, extra dependencies, and README customization despite accepting them. Verified with CLI 5.199.0 and 5.217.2. An unpinned private preview with CLI 5.217.2 selected Python generator 6.18.0 and reproduced the same behavior: the manifest contains the requested settings, but the generated package still declares Python >=3.9, omits the additional dependencies and TUS extra, and emits generic README content. Upgrading the CLI or generator alone did not remove the need for the fallbacks. Keep the packaging Replay corrections and owned README until a regeneration reproduces those settings and passes the distribution checks. The public/generated client split and additional initializer exports are supported.
