"""Execution controls address one resource and reject retired bulk inputs."""

import inspect
import importlib.util
import json
import re

import httpx
import pytest

from harbor_client import types
from harbor_client.validation import async_client, sync_client
from test_contract import SPEC, UUID, response_fixture

CONTROLS = [
    (namespace, action)
    for namespace in ("jobs", "trials", "rollouts")
    for action in ("pause", "resume", "cancel", "retry")
    if namespace != "jobs" or action != "retry"
]


def control_path(namespace, action):
    return f"/v1/{namespace}/{{{namespace[:-1]}_id}}/{action}"


def control_arguments(namespace):
    return {f"{namespace[:-1]}_id": UUID, "idempotency_key": "opaque-key"}


async def invoke(namespace, action, arguments, handler, asynchronous):
    transport = httpx.MockTransport(handler)
    if asynchronous:
        async with async_client(transport=transport) as client:
            return await getattr(getattr(client, namespace), action)(**arguments)
    with sync_client(transport=transport) as client:
        return getattr(getattr(client, namespace), action)(**arguments)


@pytest.mark.parametrize("namespace,action", CONTROLS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_execution_controls_send_one_path_id_and_decode_typed_results(
    namespace, action, asynchronous
):
    path = control_path(namespace, action)
    payload = response_fixture(path, "post")
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url.path.endswith(f"/v1/{namespace}/{UUID}/{action}")
        assert request.headers["idempotency-key"] == "opaque-key"
        if action == "cancel":
            assert json.loads(request.content) in ({}, {"force": True})
        else:
            assert not request.content
        return httpx.Response(200, json=payload)

    result = await invoke(
        namespace, action, control_arguments(namespace), handler, asynchronous
    )
    assert len(seen) == 1
    assert result.model_dump(mode="json", exclude_unset=True) == payload


@pytest.mark.parametrize("namespace,action", CONTROLS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_controls_reject_bulk_arguments_before_network(
    namespace, action, asynchronous
):
    arguments = control_arguments(namespace)
    arguments[f"{namespace[:-1]}_ids"] = [UUID]
    with pytest.raises(TypeError):
        await invoke(
            namespace,
            action,
            arguments,
            lambda request: pytest.fail("Retired bulk input reached the network"),
            asynchronous,
        )


@pytest.mark.parametrize("namespace,action", CONTROLS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_all_controls_require_an_idempotency_key(namespace, action, asynchronous):
    arguments = {f"{namespace[:-1]}_id": UUID}
    with pytest.raises(TypeError):
        await invoke(
            namespace,
            action,
            arguments,
            lambda request: pytest.fail("Control without a key reached the network"),
            asynchronous,
        )


@pytest.mark.parametrize("namespace", ["jobs", "trials", "rollouts"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("force", [False, True])
async def test_single_resource_cancellation_preserves_explicit_force(
    namespace, asynchronous, force
):
    seen = []
    payload = response_fixture(control_path(namespace, "cancel"), "post")

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(200, json=payload)

    await invoke(
        namespace,
        "cancel",
        {**control_arguments(namespace), "force": force},
        handler,
        asynchronous,
    )
    assert seen == [{"force": force}]


@pytest.mark.parametrize("namespace,action", CONTROLS)
def test_control_contracts_and_signatures_have_no_bulk_inputs(namespace, action):
    singular_id = f"{namespace[:-1]}_id"
    path = control_path(namespace, action)
    assert f"/v1/{namespace}/{action}" not in SPEC["paths"]
    assert SPEC["paths"][path]["post"]["operationId"] == f"{namespace}.{action}"
    with sync_client(transport=httpx.MockTransport(lambda request: None)) as client:
        signature = inspect.signature(getattr(getattr(client, namespace), action))
        assert singular_id in signature.parameters
        assert f"{namespace[:-1]}_ids" not in signature.parameters
        assert (
            signature.parameters["idempotency_key"].default is inspect.Parameter.empty
        )


@pytest.mark.parametrize(
    "name",
    [
        "CancelJobsRequest",
        "CancelTrialsRequest",
        "CancelRolloutsRequest",
        "JobActionRequest",
        "JobActionResponse",
        "TrialActionRequest",
        "TrialActionResponse",
        "RolloutActionRequest",
        "RetryTrialsRequest",
        "RetryTrialsResponse",
        "RetryRolloutsRequest",
        "RetryRolloutsResponse",
    ],
)
def test_retired_bulk_models_are_not_public_exports(name):
    assert name not in SPEC["components"]["schemas"]
    with pytest.raises(AttributeError):
        getattr(types, name)
    module = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    assert importlib.util.find_spec(f"harbor_client.types.{module}") is None


def test_submission_success_requires_only_the_job_id():
    model = types.SubmitJobResponse.model_validate({"job_id": UUID})
    assert model.model_dump(mode="json", exclude_unset=True) == {"job_id": UUID}
    assert SPEC["components"]["schemas"]["SubmitJobResponse"]["required"] == ["job_id"]
