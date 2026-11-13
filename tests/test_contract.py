"""Exact wire-contract enforcement around unmodified generated Fern operations."""

import asyncio
import json
import re
from pathlib import Path
from threading import Event

import httpx
import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError as ModelValidationError

from harbor_client.net.transport.api_error import ApiError
from harbor_client.validation import (
    _schema,
    ContractError,
    ContractTransport,
    async_client,
    sync_client,
)

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[1]

SPEC = _schema()
UUID = "00000000-0000-4000-8000-000000000001"
BASE = "https://api.harborframework.com/functions/v1/api"


def example(schema, allow_null=True):
    """Construct synthetic response fixtures, then validate them against the spec."""
    if "$ref" in schema:
        return example(
            SPEC["components"]["schemas"][schema["$ref"].split("/")[-1]], allow_null
        )
    if "anyOf" in schema:
        options = schema["anyOf"]
        chosen = (
            next((s for s in options if s.get("type") == "null"), options[0])
            if allow_null
            else next(s for s in options if s.get("type") != "null")
        )
        return example(chosen)
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        return {
            name: example(schema["properties"][name])
            for name in schema.get("required", [])
        }
    if kind == "array":
        return [example(schema["items"]) for _ in range(schema.get("minItems", 0))]
    if kind == "string":
        candidates = (
            [UUID, "2026-11-06T12:00:00Z", "a" * 64, "example", "0"]
            if schema.get("pattern")
            else ["example"]
        )
        return next(
            s
            for s in candidates
            if len(s) >= schema.get("minLength", 0)
            and re.search(schema.get("pattern", ""), s)
        )
    if kind in {"integer", "number"}:
        return max(0, schema.get("minimum", 0))
    if kind == "boolean":
        return False
    return None


def response_fixture(path, method="get"):
    schema = SPEC["paths"][path][method]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    data = example(schema, allow_null=False)
    Draft202012Validator({**SPEC, **schema}).validate(data)
    return data


def submit_request(config):
    schema = SPEC["paths"]["/v1/jobs/submit"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    payload = example(schema, allow_null=False)
    payload.update(config=config, idempotency_key="test")
    return payload


@pytest.mark.parametrize(
    "operation", ["submit", "preflight-direct", "preflight-gateway"]
)
@pytest.mark.parametrize("field", ["secret_bindings", "secret_tags"])
@pytest.mark.parametrize("value", [None, [], "sensitive-value"])
def test_checked_operations_reject_forbidden_fields_before_network(
    operation, field, value
):
    def handler(request):
        pytest.fail("Invalid input reached the HTTP transport")

    config = {"agents": [{"name": "oracle", field: value}]}
    with sync_client(token="key", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises((ContractError, ModelValidationError, TypeError)) as error:
            if operation == "submit":
                client.jobs.submit(**submit_request(config))
            else:
                config["credential_mode"] = operation.removeprefix("preflight-")
                client.secrets.preflight(config=config)
    if isinstance(error.value, TypeError):
        # Fern wraps Pydantic errors; reject unrelated signature errors.
        assert field in str(error.value)
    assert "sensitive-value" not in str(error.value)


def test_open_agent_config_stays_open_and_valid_submission_works():
    sent = []
    payload = response_fixture("/v1/jobs/submit", "post")

    def handler(request):
        sent.append(json.loads(request.content))
        return httpx.Response(200, json=payload)

    with sync_client(token="key", transport=httpx.MockTransport(handler)) as client:
        client.jobs.submit(
            **submit_request(
                {"agents": [{"name": "oracle", "future_field": {"allowed": True}}]}
            )
        )
    assert sent[0]["config"]["agents"][0]["future_field"] == {"allowed": True}


@pytest.mark.parametrize("value", [0, "invalid", [], True])
def test_non_object_detail_data_is_rejected_before_generated_decoder(value):
    payload = response_fixture("/v1/trials/{trial_id}")
    payload["trial"]["result"] = value
    with sync_client(
        token="key",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload)
        ),
    ) as client:
        with pytest.raises(ContractError, match="response body"):
            client.trials.get(trial_id=UUID)


def test_required_nullable_response_accepts_null_and_a_real_detail():
    payload = response_fixture("/v1/trials/{trial_id}")
    assert payload["trial"]["result"] is None
    with sync_client(
        token="key",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json=payload)
        ),
    ) as client:
        detail = client.trials.get(trial_id=UUID)
    assert detail.trial.result is None


def test_checked_reads_send_auth_and_preserve_empty_strings_and_opaque_cursors():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200, json={"items": [], "total": 0, "next_page_token": "opaque/+=token"}
        )

    with sync_client(token="key", transport=httpx.MockTransport(handler)) as client:
        pager = client.jobs.list(q="", page_token="opaque/+=token")
        assert next(pager.iter_pages()) == []
        assert pager.last_response.body["total"] == 0
    assert requests[0].headers["authorization"] == "Bearer key"
    assert requests[0].url.params["q"] == ""
    assert requests[0].url.params["page_token"] == "opaque/+=token"


@pytest.mark.parametrize("total", [True, "0"])
def test_known_response_types_are_strict_without_rejecting_future_fields(total):
    payload = {"items": [], "total": total, "next_page_token": "", "future_field": True}
    with sync_client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    ) as client:
        with pytest.raises(ContractError):
            list(client.jobs.list())
    payload["total"] = 0
    with sync_client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    ) as client:
        assert list(client.jobs.list()) == []


@pytest.mark.parametrize(
    "options",
    [
        {"state": "invalid"},
        {
            "request_options": {"additional_headers": {"Harbor-API-Version": "wrong"}},
        },
    ],
)
def test_invalid_query_and_header_rejected_before_network(options):
    with sync_client(
        transport=httpx.MockTransport(
            lambda request: pytest.fail("Invalid request reached network")
        )
    ) as client:
        with pytest.raises(ContractError):
            list(client.jobs.list(**options))


def test_checked_mutations_are_never_automatically_retried():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(503, json={})

    with sync_client(token="key", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ApiError):
            client.api_keys.revoke(key_id="key")
    assert len(requests) == 1


@pytest.mark.parametrize("failure", [False, True])
def test_one_pool_is_reused_and_closed_even_on_failure(failure):
    class Pool(httpx.MockTransport):
        closed = False

        def close(self):
            self.closed = True

    pool = Pool(
        lambda request: httpx.Response(
            200, json={"items": [], "total": 0, "next_page_token": ""}
        )
    )
    try:
        with sync_client(transport=pool) as client:
            list(client.jobs.list())
            list(client.jobs.list())
            if failure:
                raise RuntimeError("caller failed")
    except RuntimeError:
        if not failure:
            raise
    assert pool.closed


async def test_async_checked_client_reuses_the_same_contract_transport():
    with_requests = []

    def handler(request):
        with_requests.append(request)
        return httpx.Response(
            200, json={"items": [], "total": 0, "next_page_token": ""}
        )

    async with async_client(
        token="key", transport=httpx.MockTransport(handler)
    ) as client:
        pager = client.jobs.list()
        assert await anext(pager.iter_pages()) == []
        assert pager.last_response.body["total"] == 0
    assert with_requests[0].headers["authorization"] == "Bearer key"


async def test_cancelled_async_workflow_waits_for_inflight_request_before_closing_pool():
    started, release, closed = Event(), Event(), Event()

    def handler(request):
        started.set()
        if not release.wait(2):
            pytest.fail("Request was not released")
        assert not closed.is_set()
        return httpx.Response(
            200, json={"items": [], "total": 0, "next_page_token": ""}
        )

    class Pool(httpx.MockTransport):
        def close(self):
            closed.set()

    async def workflow():
        async with async_client(transport=Pool(handler)) as client:
            await anext(client.jobs.list().iter_pages())

    task = asyncio.create_task(workflow())
    try:
        assert await asyncio.to_thread(started.wait, 2)
        task.cancel()
        await asyncio.sleep(0)
        assert not closed.is_set()
    finally:
        release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert closed.is_set()


def test_invalid_response_closes_its_body_and_rejects_content_type():
    closed = []

    class Body(httpx.SyncByteStream):
        def __iter__(self):
            yield b'{"items": []}'

        def close(self):
            closed.append(True)

    with sync_client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, headers={"content-type": "text/plain"}, stream=Body()
            )
        )
    ) as client:
        with pytest.raises(ValueError, match="content type"):
            list(client.jobs.list())
    assert closed


def test_checked_transport_rejects_undocumented_origins_and_routes():
    with httpx.Client(
        transport=ContractTransport(
            httpx.MockTransport(
                lambda request: pytest.fail("Unknown route reached network")
            )
        )
    ) as http:
        for url in ["https://other.example/v1/jobs", BASE + "/v1/unknown"]:
            with pytest.raises(ValueError):
                http.get(url)


def test_resource_path_parameters_are_validated_before_network():
    with sync_client(
        transport=httpx.MockTransport(
            lambda request: pytest.fail("Invalid path reached network")
        )
    ) as client:
        with pytest.raises(ContractError, match="path parameter"):
            client.jobs.get(job_id="invalid-uuid")


def test_static_resource_routes_take_precedence_over_identifier_templates():
    payload = response_fixture("/v1/jobs/overview")
    with sync_client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    ) as client:
        client.jobs.get_overview(job_ids=UUID)

    payload = response_fixture("/v1/organizations/by-name/{name}")
    with sync_client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    ) as client:
        client.organizations.get_by_name(name="permissions")


def test_encoded_slash_remains_one_logical_path_parameter():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "protocol": "http",
                "method": "GET",
                "url": "https://storage.example/signed",
                "headers": {},
                "expires_at": "2099-01-01T00:00:00Z",
                "version": "version",
                "size_bytes": 5,
            },
        )

    with sync_client(transport=httpx.MockTransport(handler)) as client:
        client.packages.download_file(version_id=UUID, file="folder/file.txt")
    assert b"folder%2Ffile.txt" in requests[0].url.raw_path


def test_checked_client_follows_a_new_contract_version(tmp_path, monkeypatch):
    import gzip
    import importlib.resources
    import importlib.util
    import harbor_client.validation as validation

    old_version = SPEC["info"]["version"]
    new_version = "2099-01-01.preview"

    def replace_version(value):
        if isinstance(value, dict):
            return {key: replace_version(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace_version(item) for item in value]
        return new_version if value == old_version else value

    (tmp_path / "_openapi.json.gz").write_bytes(
        gzip.compress(json.dumps(replace_version(SPEC)).encode())
    )
    original_files = importlib.resources.files
    monkeypatch.setattr(
        importlib.resources,
        "files",
        lambda package: (
            tmp_path if package == "harbor_client" else original_files(package)
        ),
    )
    module_spec = importlib.util.spec_from_file_location(
        "harbor_client._future_contract_validation", validation.__file__
    )
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    sent = []

    def handler(request):
        sent.append(request)
        return httpx.Response(200, json=response_fixture("/v1/api-keys"))

    with module.sync_client(
        token="key", transport=httpx.MockTransport(handler)
    ) as client:
        next(client.api_keys.list().iter_pages())
    assert sent[0].headers["Harbor-API-Version"] == new_version
