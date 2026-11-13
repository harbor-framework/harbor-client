# Reference

## OrganizationsClient

### `client.organizations.get`

`GET /v1/organizations/{organization_id}`

**Parameters:**

- `organization_id` (required)

### `client.organizations.get_by_name`

`GET /v1/organizations/by-name/{name}`

**Parameters:**

- `name` (required)

### `client.organizations.ensure`

`POST /v1/organizations`

## PackagesClient

### `client.packages.set_visibility`

`PATCH /v1/packages/{organization_name}/{name}/visibility`

**Parameters:**

- `organization_name` (required)
- `name` (required)

### `client.packages.update_organization_access`

`PATCH /v1/packages/{organization_name}/{name}/access/organizations/{target_organization_id}`

**Parameters:**

- `organization_name` (required)
- `name` (required)
- `target_organization_id` (required)

### `client.packages.get_access`

`GET /v1/packages/{organization_name}/{name}/access`

**Parameters:**

- `organization_name` (required)
- `name` (required)

### `client.packages.get_version`

`GET /v1/packages/{organization_name}/{name}/versions/{ref}`

**Parameters:**

- `organization_name` (required)
- `name` (required)
- `ref` (required)

### `client.packages.get_version_manifest`

`GET /v1/packages/{organization_name}/{name}/versions/{ref}/manifest`

**Parameters:**

- `organization_name` (required)
- `name` (required)
- `ref` (required)

### `client.packages.list_version_files`

`GET /v1/packages/{organization_name}/{name}/versions/{ref}/files`

**Parameters:**

- `organization_name` (required)
- `name` (required)
- `ref` (required)
- `page_size`
- `page_token`
- `offset`

### `client.packages.list_tags`

`GET /v1/packages/{organization_name}/{name}/tags`

**Parameters:**

- `organization_name` (required)
- `name` (required)

### `client.packages.tag_version`

`PUT /v1/packages/{organization_name}/{name}/tags/{tag}`

**Parameters:**

- `organization_name` (required)
- `name` (required)
- `tag` (required)

### `client.packages.reserve_temporary_task`

`POST /v1/packages/reserve-temporary`

### `client.packages.get_private_task_count`

`GET /v1/packages/{organization_name}/{name}/private-task-count`

**Parameters:**

- `organization_name` (required)
- `name` (required)

### `client.packages.list_version_catalog`

`GET /v1/packages/versions`

**Parameters:**

- `type` (required)
- `page_size`
- `page_token`
- `offset`
- `organization_id`
- `include_yanked`

### `client.packages.get`

`GET /v1/packages/{organization_name}/{name}`

**Parameters:**

- `organization_name` (required)
- `name` (required)

### `client.packages.list_versions`

`GET /v1/packages/{organization_name}/{name}/versions`

**Parameters:**

- `organization_name` (required)
- `name` (required)
- `page_size`
- `page_token`
- `include_yanked`

### `client.packages.download_archive`

`GET /v1/packages/versions/{version_id}/archive`

**Parameters:**

- `version_id` (required)
- `transfer_id`
- `dataset_version_id`

### `client.packages.download_file`

`GET /v1/packages/versions/{version_id}/files/{file}`

**Parameters:**

- `version_id` (required)
- `file` (required)
- `transfer_id`

## JobsClient

### `client.jobs.get_sharing`

`GET /v1/jobs/{job_id}/shares`

**Parameters:**

- `job_id` (required)

### `client.jobs.update_sharing`

`PATCH /v1/jobs/{job_id}/shares`

**Parameters:**

- `job_id` (required)

### `client.jobs.get_trial_status`

`GET /v1/jobs/{job_id}/trial-status`

**Parameters:**

- `job_id` (required)

### `client.jobs.get`

`GET /v1/jobs/{job_id}`

**Parameters:**

- `job_id` (required)

### `client.jobs.rename`

`PATCH /v1/jobs/{job_id}`

**Parameters:**

- `job_id` (required)

### `client.jobs.get_artifact_download`

`GET /v1/jobs/{job_id}/artifacts`

**Parameters:**

- `job_id` (required)
- `artifact_type` (required)

### `client.jobs.submit`

`POST /v1/jobs/submit`

**Parameters:**

- `idempotency_key` (required)

### `client.jobs.delete`

`POST /v1/jobs/delete`

### `client.jobs.transfer`

`POST /v1/jobs/{job_id}/transfer`

**Parameters:**

- `job_id` (required)

### `client.jobs.copy`

`POST /v1/jobs/{source_job_id}/copy`

**Parameters:**

- `source_job_id` (required)

### `client.jobs.pause`

`POST /v1/jobs/{job_id}/pause`

**Parameters:**

- `job_id` (required)
- `idempotency_key` (required)

### `client.jobs.resume`

`POST /v1/jobs/{job_id}/resume`

**Parameters:**

- `job_id` (required)
- `idempotency_key` (required)

### `client.jobs.cancel`

`POST /v1/jobs/{job_id}/cancel`

**Parameters:**

- `job_id` (required)
- `idempotency_key` (required)

### `client.jobs.list`

`GET /v1/jobs`

**Parameters:**

- `task`
- `state`
- `name`
- `q`
- `agent_name`
- `agent_version`
- `model_name`
- `model_provider`
- `reasoning_effort`
- `source`
- `created_after`
- `created_before`
- `page_size`
- `page_token`
- `sort`

### `client.jobs.get_filters`

`GET /v1/jobs/filters`

**Parameters:**

- `field` (required)
- `task`
- `state`
- `name`
- `q`
- `agent_name`
- `agent_version`
- `model_name`
- `model_provider`
- `reasoning_effort`
- `source`
- `created_after`
- `created_before`
- `limit`

### `client.jobs.list_tasks`

`GET /v1/jobs/{job_id}/tasks`

**Parameters:**

- `job_id` (required)
- `page_size`
- `page_token`
- `offset`
- `search`
- `agents`
- `providers`
- `models`
- `tasks`
- `sort_by`
- `sort_order`

### `client.jobs.import_results`

`POST /v1/jobs/import`

### `client.jobs.get_overview`

`GET /v1/jobs/overview`

**Parameters:**

- `job_ids` (required)
- `force_combined`

### `client.jobs.get_comparison`

`GET /v1/jobs/comparisons`

**Parameters:**

- `job_ids` (required)

## TrialsClient

### `client.trials.get`

`GET /v1/trials/{trial_id}`

**Parameters:**

- `trial_id` (required)

### `client.trials.list`

`GET /v1/trials`

**Parameters:**

- `task`
- `state`
- `name`
- `q`
- `agent_name`
- `agent_version`
- `model_name`
- `model_provider`
- `reasoning_effort`
- `source`
- `created_after`
- `created_before`
- `job_id`
- `page_size`
- `page_token`
- `sort`

### `client.trials.create`

`POST /v1/trials`

### `client.trials.get_filters`

`GET /v1/trials/filters`

**Parameters:**

- `field` (required)
- `task`
- `state`
- `name`
- `q`
- `agent_name`
- `agent_version`
- `model_name`
- `model_provider`
- `reasoning_effort`
- `source`
- `created_after`
- `created_before`
- `job_id`
- `limit`

### `client.trials.pause`

`POST /v1/trials/{trial_id}/pause`

Pause this physical trial. Reusing the same Idempotency-Key does not reapply the command.

**Parameters:**

- `trial_id` (required)
- `idempotency_key` (required)

### `client.trials.resume`

`POST /v1/trials/{trial_id}/resume`

Resume this physical trial. Reusing the same Idempotency-Key does not reapply the command.

**Parameters:**

- `trial_id` (required)
- `idempotency_key` (required)

### `client.trials.cancel`

`POST /v1/trials/{trial_id}/cancel`

Cancel this physical trial. Reusing the same Idempotency-Key does not reapply the command. force defaults to true; false lets a running attempt finish.

**Parameters:**

- `trial_id` (required)
- `idempotency_key` (required)

### `client.trials.retry`

`POST /v1/trials/{trial_id}/retry`

Retry this physical trial. Reusing the same Idempotency-Key does not reapply the command. The latest terminal attempt is required; replays return the originally created attempt ID.

**Parameters:**

- `trial_id` (required)
- `idempotency_key` (required)

### `client.trials.get_artifact_download`

`GET /v1/trials/{trial_id}/artifacts`

**Parameters:**

- `trial_id` (required)
- `artifact_type` (required)

### `client.trials.copy`

`POST /v1/trials/{source_trial_id}/copy`

**Parameters:**

- `source_trial_id` (required)

## RolloutsClient

### `client.rollouts.get`

`GET /v1/rollouts/{rollout_id}`

**Parameters:**

- `rollout_id` (required)

### `client.rollouts.list`

`GET /v1/rollouts`

**Parameters:**

- `task`
- `state`
- `name`
- `q`
- `agent_name`
- `agent_version`
- `model_name`
- `model_provider`
- `reasoning_effort`
- `source`
- `created_after`
- `created_before`
- `job_id`
- `page_size`
- `page_token`
- `sort`

### `client.rollouts.get_filters`

`GET /v1/rollouts/filters`

**Parameters:**

- `field` (required)
- `task`
- `state`
- `name`
- `q`
- `agent_name`
- `agent_version`
- `model_name`
- `model_provider`
- `reasoning_effort`
- `source`
- `created_after`
- `created_before`
- `job_id`
- `limit`

### `client.rollouts.pause`

`POST /v1/rollouts/{rollout_id}/pause`

Pause this physical rollout. Reusing the same Idempotency-Key does not reapply the command.

**Parameters:**

- `rollout_id` (required)
- `idempotency_key` (required)

### `client.rollouts.resume`

`POST /v1/rollouts/{rollout_id}/resume`

Resume this physical rollout. Reusing the same Idempotency-Key does not reapply the command.

**Parameters:**

- `rollout_id` (required)
- `idempotency_key` (required)

### `client.rollouts.cancel`

`POST /v1/rollouts/{rollout_id}/cancel`

Cancel this physical rollout. Reusing the same Idempotency-Key does not reapply the command. force defaults to true; false lets a running attempt finish.

**Parameters:**

- `rollout_id` (required)
- `idempotency_key` (required)

### `client.rollouts.retry`

`POST /v1/rollouts/{rollout_id}/retry`

Retry this physical rollout. Reusing the same Idempotency-Key does not reapply the command. The latest terminal attempt is required; replays return the originally created attempt ID.

**Parameters:**

- `rollout_id` (required)
- `idempotency_key` (required)

## AccountClient

### `client.account.get`

`GET /v1/account`

### `client.account.list_organization_memberships`

`GET /v1/account/organization-memberships`

## ApiKeysClient

### `client.api_keys.list`

`GET /v1/api-keys`

**Parameters:**

- `page_size`
- `page_token`

### `client.api_keys.create`

`POST /v1/api-keys`

Create a personal API key using a signed-in user session. Harbor API keys and exchanged API-key JWTs cannot create keys. The raw key is returned once. Do not retry an ambiguous creation response.

### `client.api_keys.revoke`

`POST /v1/api-keys/{key_id}/revoke`

**Parameters:**

- `key_id` (required)

## AgentsClient

### `client.agents.list`

`GET /v1/agents`

### `client.agents.get_options`

`GET /v1/agents/{name}/options`

**Parameters:**

- `name` (required)

## LeaderboardsClient

### `client.leaderboards.get`

`GET /v1/leaderboards/{leaderboard_id}`

**Parameters:**

- `leaderboard_id` (required)

### `client.leaderboards.update`

`PATCH /v1/leaderboards/{leaderboard_id}`

**Parameters:**

- `leaderboard_id` (required)

### `client.leaderboards.resolve`

`GET /v1/leaderboards/resolve`

**Parameters:**

- `package` (required)
- `name` (required)

### `client.leaderboards.get_row`

`GET /v1/leaderboards/rows/{row_id}`

**Parameters:**

- `row_id` (required)

### `client.leaderboards.list_rows`

`GET /v1/leaderboards/rows`

**Parameters:**

- `leaderboard_id`
- `package`
- `name`
- `page_size`
- `page_token`
- `row_ids`

### `client.leaderboards.list`

`GET /v1/leaderboards`

**Parameters:**

- `page_size`
- `page_token`
- `package`
- `dataset_version_id`

### `client.leaderboards.create`

`POST /v1/leaderboards`

### `client.leaderboards.list_trials`

`GET /v1/leaderboards/rows/{row_id}/trials`

**Parameters:**

- `row_id` (required)
- `page_size`
- `page_token`

## SecretsClient

### `client.secrets.list`

`GET /v1/secrets`

**Parameters:**

- `organization_id`
- `job_id`
- `status_filter`
- `page_size`
- `page_token`
- `offset`

### `client.secrets.upsert`

`POST /v1/secrets`

### `client.secrets.revoke`

`POST /v1/secrets/revoke`

### `client.secrets.preflight`

`POST /v1/secrets/preflight`

### `client.secrets.list_registry_credentials`

`GET /v1/secrets/registry-credentials`

**Parameters:**

- `organization_id`
- `status`

### `client.secrets.upsert_registry_credential`

`POST /v1/secrets/registry-credentials`

### `client.secrets.revoke_registry_credential`

`DELETE /v1/secrets/registry-credentials/{credential_id}`

**Parameters:**

- `credential_id` (required)
- `purge`

## StorageClient

### `client.storage.create_upload`

`POST /v1/storage/uploads`

### `client.storage.complete_upload`

`POST /v1/storage/uploads/{upload_id}/complete`

**Parameters:**

- `upload_id` (required)
