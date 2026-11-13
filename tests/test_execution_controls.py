"""Execution controls use ID arrays and reject retired selector bodies."""

import json

import httpx
import pytest
from pydantic import ValidationError

from harbor_client import types
from harbor_client.validation import ContractError, async_client, sync_client
from test_contract import SPEC, UUID, response_fixture

CONTROLS = [
    (namespace, action)
    for namespace in ("jobs", "trials", "rollouts")
    for action in ("pause", "resume", "cancel", "retry")
    if namespace != "jobs" or action != "retry"
]


def control_arguments(namespace, action, ids):
    result = {f"{namespace[:-1]}_ids": ids}
    if action == "retry":
        result["idempotency_key"] = "opaque-key"
    return result


@pytest.mark.parametrize("namespace,action", CONTROLS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_execution_controls_send_arrays_and_decode_typed_results(
    namespace, action, asynchronous
):
    path = f"/v1/{namespace}/{action}"
    payload = response_fixture(path, "post")
    seen = []

    def handler(request):
        body = json.loads(request.content)
        seen.append(body)
        assert body[f"{namespace[:-1]}_ids"] == [UUID]
        assert request.url.path.endswith(path)
        if action == "retry":
            assert request.headers["idempotency-key"] == "opaque-key"
        return httpx.Response(200, json=payload)

    arguments = control_arguments(namespace, action, [UUID])
    transport = httpx.MockTransport(handler)
    if asynchronous:
        async with async_client(transport=transport) as client:
            result = await getattr(getattr(client, namespace), action)(**arguments)
    else:
        with sync_client(transport=transport) as client:
            result = getattr(getattr(client, namespace), action)(**arguments)
    assert len(seen) == 1
    assert result.model_dump(mode="json", exclude_unset=True) == payload


@pytest.mark.parametrize("namespace,action", CONTROLS)
@pytest.mark.parametrize("ids", [[], "all", {"all": True}, [None], [123]])
def test_execution_controls_reject_invalid_arrays_before_network(
    namespace, action, ids
):
    with sync_client(
        transport=httpx.MockTransport(
            lambda request: pytest.fail("Invalid array reached the network")
        )
    ) as client:
        with pytest.raises((ContractError, ValidationError, TypeError)):
            getattr(getattr(client, namespace), action)(
                **control_arguments(namespace, action, ids)
            )


@pytest.mark.parametrize("namespace,action", CONTROLS)
@pytest.mark.parametrize("selector", [{"all": True}, {"filters": {}}, {"scope": "my"}])
def test_execution_controls_reject_extra_selector_fields(namespace, action, selector):
    with sync_client(
        transport=httpx.MockTransport(
            lambda request: pytest.fail("Retired selector reached the network")
        )
    ) as client:
        with pytest.raises(ContractError):
            getattr(getattr(client, namespace), action)(
                **control_arguments(namespace, action, [UUID]),
                request_options={"additional_body_parameters": selector},
            )


def test_submission_success_requires_only_the_job_id():
    model = types.SubmitJobResponse.model_validate({"job_id": UUID})
    assert model.model_dump(mode="json", exclude_unset=True) == {"job_id": UUID}
    assert SPEC["components"]["schemas"]["SubmitJobResponse"]["required"] == ["job_id"]
