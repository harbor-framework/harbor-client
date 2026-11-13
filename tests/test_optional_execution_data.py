"""Portable execution detail data is a required nullable JSON-object envelope."""

from copy import deepcopy

import httpx
import pytest
from pydantic import ValidationError

from harbor_client import AsyncHarborAPIClient, HarborAPIClient
from harbor_client.validation import ContractError, async_client, sync_client
from test_contract import SPEC, UUID, response_fixture

DETAILS = [("trials", "trial", "trial_id"), ("rollouts", "rollout", "rollout_id")]
OBJECT_DATA = {
    "result": {
        "id": UUID,
        "task_name": "example-task",
        "verifier_result": {"rewards": {"accuracy": None, "coverage": 0.5}},
        "agent_result": {"n_input_tokens": 0, "metadata": {"continued": False}},
    },
    "storage_error": {
        "exception_type": "FileNotFoundError",
        "exception_message": "Artifact was unavailable",
        "exception_traceback": "Traceback: FileNotFoundError",
    },
}


def detail_payload(resource, wrapper, id_field, data):
    payload = response_fixture(f"/v1/{resource}/{{{id_field}}}")
    payload[wrapper].update(deepcopy(data))
    return payload


async def get_detail(client, resource, wrapper, id_field, asynchronous):
    result = getattr(client, resource).get(**{id_field: UUID})
    if asynchronous:
        result = await result
    return getattr(result, wrapper)


async def parse_detail(resource, wrapper, id_field, payload, asynchronous, checked):
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    if checked:
        if asynchronous:
            async with async_client(transport=transport) as client:
                return await get_detail(
                    client, resource, wrapper, id_field, asynchronous
                )
        with sync_client(transport=transport) as client:
            return await get_detail(client, resource, wrapper, id_field, asynchronous)
    with httpx.Client(transport=transport) as http:
        cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
        client = cls(harbor_api_version=SPEC["info"]["version"], httpx_client=http)
        return await get_detail(client, resource, wrapper, id_field, asynchronous)


@pytest.mark.parametrize("resource,wrapper,id_field", DETAILS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("checked", [False, True], ids=["native", "checked"])
@pytest.mark.parametrize(
    "data",
    [
        {"result": None, "storage_error": None},
        {"result": {}, "storage_error": {}},
        OBJECT_DATA,
    ],
)
async def test_optional_execution_detail_data_accepts_null_and_objects(
    resource, wrapper, id_field, asynchronous, checked, data
):
    payload = detail_payload(resource, wrapper, id_field, data)
    detail = await parse_detail(
        resource, wrapper, id_field, payload, asynchronous, checked
    )
    assert detail.result == data["result"]
    assert detail.storage_error == data["storage_error"]
    dumped = detail.model_dump(mode="json")
    assert dumped["result"] == data["result"]
    assert dumped["storage_error"] == data["storage_error"]


@pytest.mark.parametrize("resource,wrapper,id_field", DETAILS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("checked", [False, True], ids=["native", "checked"])
@pytest.mark.parametrize("field", ["result", "storage_error"])
@pytest.mark.parametrize("value", [True, 0, 0.5, "invalid", [], [{}]])
async def test_optional_execution_detail_data_rejects_non_objects(
    resource, wrapper, id_field, asynchronous, checked, field, value
):
    payload = detail_payload(resource, wrapper, id_field, {field: value})
    with pytest.raises(ContractError if checked else ValidationError):
        await parse_detail(resource, wrapper, id_field, payload, asynchronous, checked)


@pytest.mark.parametrize("resource,wrapper,id_field", DETAILS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("checked", [False, True], ids=["native", "checked"])
@pytest.mark.parametrize("field", ["result", "storage_error"])
async def test_nullable_execution_detail_fields_remain_required(
    resource, wrapper, id_field, asynchronous, checked, field
):
    payload = detail_payload(resource, wrapper, id_field, {})
    del payload[wrapper][field]
    with pytest.raises(ContractError if checked else ValidationError):
        await parse_detail(resource, wrapper, id_field, payload, asynchronous, checked)
