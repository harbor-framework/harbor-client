# Harbor API Python SDK

Install the independently versioned `harbor-client` package and use `HarborAPIClient` or `AsyncHarborAPIClient`. A package release has not been published yet; development consumers pin this repository to a commit.

```python
from harbor_client.validation import sync_client

with sync_client(token="your-api-key") as client:
    for job in client.jobs.list():
        print(job.id, job.name)
```

## Regeneration

The API implementation owns the public OpenAPI document. This repository keeps its input snapshot and Fern configuration; the scheduled generation workflow checks for changes daily and can also be run manually. Fern opens SDK update pull requests against this repository. It owns generation commits, customization detection, three-way merging, and `.fern/replay.lock`. Review the generated changes and CI results before merging.

Commit necessary edits to generated files normally: Fern Replay detects them on the next regeneration. Resolve conflicts with `npx fern-replay resolve .`; do not edit the lockfile by hand or accept unresolved patches. `.fernignore` protects the fully owned validation/transfer helpers, packaging support, tests, and CI. It does not freeze generated resource clients or models.

The SDK retains regression tests for all documented operations, pagination, wire validation, pooling, and signed transfers. Static export stubs are derived from Fern's model registry during the standard package build; there is no separate SDK assembly or patch-generation command.

Generation and release are separate. There is no automatic registry publication in this repository.
