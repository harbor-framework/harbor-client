# Harbor API Python SDK

Install the independently versioned `harbor-framework-client` package and use `HarborAPIClient` or `AsyncHarborAPIClient`. A package release has not been published yet; development consumers pin this repository to a commit.

```python
from harbor_client.validation import sync_client

with sync_client(token="your-api-key") as client:
    for job in client.jobs.list():
        print(job.id, job.name)
```

## Regeneration

The API implementation owns the public OpenAPI document. This repository keeps its input snapshot and Fern configuration; the scheduled generation workflow checks for changes daily and can also be run manually. Fern opens SDK update pull requests against this repository. It owns generation commits, customization detection, three-way merging, and `.fern/replay.lock`. Review the generated changes and CI results before merging.

For an unmerged API candidate, commit its OpenAPI document to `fern/openapi.json` on an SDK preview branch and run the workflow with `spec_ref` set to that branch. Alternatively supply `spec_url` for an HTTPS document. `sdk_branch` selects the base branch for Fern's update PR; it defaults to `main`. The workflow uses the same pinned SDK profile and attaches the exact selected contract. Checked-client API version defaults follow that contract automatically. No API deployment is needed. Whitespace or object-key ordering changes alone do not trigger regeneration. The scheduled source URL can be changed through the `OPENAPI_SPEC_URL` repository variable.

Review Fern's proposed version and changelog before merging. In the pinned publisher, AUTO can classify preserved Replay customizations as removals. Use `sdk_version` to rerun generation with the intended version when needed; this uses Fern's version flag and updates all generated version metadata together. No custom versioning engine is used.

Commit necessary edits to generated files normally: Fern Replay detects them on the next regeneration. Resolve conflicts with `npx fern-replay resolve .`; do not edit the lockfile by hand or accept unresolved patches. `.fernignore` protects the fully owned validation/transfer helpers, packaging support, tests, and CI. It does not freeze generated resource clients or models.

The SDK retains regression tests for all documented operations, pagination, wire validation, pooling, and signed transfers. Static export stubs are derived from Fern's model registry during the standard package build; there is no separate SDK assembly or patch-generation command.

Generation and release are separate. After an SDK update is reviewed and merged, publish a GitHub release tagged `v<package version>` to run the release workflow. It requires SDK checks, builds distributions and publishes with PyPI trusted publishing. Starting the workflow manually runs verification and builds only; it never publishes. Build files and authenticated generation logs are not uploaded as Actions artifacts.

One-time PyPI setup: register `harbor-framework/harbor-client`, workflow `release.yml`, and environment `pypi` as the trusted publisher for `harbor-framework-client`. No PyPI API token is needed. Configure GitHub's `pypi` environment to restrict release deployments to the intended tags.

Fern 6.17.0's SDK Config publishing preview emitted compile/test jobs but no publish job. The release workflow therefore uses the official PyPA action, following [Fern's documented publishing fallback](https://buildwithfern.com/learn/sdks/generators/python/publishing#path-2-manual-ci-workflow-update). Generation and Replay still use Fern's native publisher.

## Ownership of custom code

Fern owns generated resource clients, models, imports and formatting. Project lint and formatting checks cover tests, packaging support and the two handwritten helper modules; they do not rewrite generated source.

The remaining customizations have behavioral regression tests:

- `validation.py` enforces JSON Schema constraints the generator does not preserve.
- `transfers.py` orchestrates signed byte transfers and resumable uploads over generated endpoint methods.
- Replay preserves pagination, URL encoding, connection lifetime and model-fidelity fixes until the generator provides them.
- `setup.py` derives static export stubs during package builds. Packaging metadata includes these stubs and the validation contract.

Avoid cosmetic edits to generated files. When an upstream fix replaces a customization, verify its regression tests and retire the obsolete patch through Fern's Replay tools.
