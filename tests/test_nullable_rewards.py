"""Nullable reward values survive typed execution models and native HTTP parsing."""

from copy import deepcopy

import httpx
import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from harbor_client import AsyncHarborAPIClient, HarborAPIClient, types
from harbor_client.validation import ContractError, async_client, sync_client
from test_contract import SPEC, UUID, example, response_fixture

VALID_REWARDS = [
    None,
    {},
    {"accuracy": None},
    {"accuracy": 0},
    {"accuracy": 0.75},
    {"score": 1, "unscored": None, "negative": -0.25},
]
INVALID_REWARDS = ["bad", [], {"accuracy": "bad"}, {"accuracy": {"nested": 1}}]
MODEL_SCHEMAS = [
    ("TrialSummary", "TrialSummary"),
    ("TrialDetail", "TrialDetail"),
]


@pytest.mark.parametrize("model_name,schema_name", MODEL_SCHEMAS)
@pytest.mark.parametrize("rewards", VALID_REWARDS)
def test_nullable_reward_models_preserve_values(model_name, schema_name, rewards):
    schema = SPEC["components"]["schemas"][schema_name]
    payload = example(schema, allow_null=False)
    payload["rewards"] = deepcopy(rewards)
    Draft202012Validator({**SPEC, **schema}).validate(payload)
    decoded = getattr(types, model_name).model_validate(payload)
    assert decoded.rewards == rewards
    assert decoded.model_dump(mode="json")["rewards"] == rewards
    del payload["rewards"]
    with pytest.raises(ValidationError):
        getattr(types, model_name).model_validate(payload)


@pytest.mark.parametrize("model_name,schema_name", MODEL_SCHEMAS)
@pytest.mark.parametrize("rewards", INVALID_REWARDS)
def test_nullable_reward_models_reject_invalid_values(model_name, schema_name, rewards):
    payload = example(SPEC["components"]["schemas"][schema_name], allow_null=False)
    payload["rewards"] = deepcopy(rewards)
    with pytest.raises(ValidationError):
        getattr(types, model_name).model_validate(payload)


READS = [
    ("trials", "list", "/v1/trials", None),
    ("rollouts", "list", "/v1/rollouts", None),
    ("trials", "get", "/v1/trials/{trial_id}", "trial"),
    ("rollouts", "get", "/v1/rollouts/{rollout_id}", "rollout"),
]


def reward_payload(path, wrapper, rewards):
    payload = response_fixture(path)
    if wrapper is None:
        item = example(SPEC["components"]["schemas"]["TrialSummary"], allow_null=False)
        payload.update(items=[item], total=1, next_page_token="")
    else:
        item = payload[wrapper]
    item["rewards"] = deepcopy(rewards)
    return payload


async def call_read(client, namespace, method, wrapper, asynchronous):
    service = getattr(client, namespace)
    if method == "list":
        pager = service.list()
        page = (
            await anext(pager.iter_pages())
            if asynchronous
            else next(pager.iter_pages())
        )
        return page[0]
    arguments = {"trial_id" if namespace == "trials" else "rollout_id": UUID}
    result = service.get(**arguments)
    if asynchronous:
        result = await result
    return getattr(result, wrapper)


@pytest.mark.parametrize("namespace,method,path,wrapper", READS)
@pytest.mark.parametrize("rewards", VALID_REWARDS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_native_execution_reads_preserve_nullable_rewards(
    namespace, method, path, wrapper, rewards, asynchronous
):
    payload = reward_payload(path, wrapper, rewards)
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url.path.endswith(path.format(trial_id=UUID, rollout_id=UUID))
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
        client = cls(harbor_api_version=SPEC["info"]["version"], httpx_client=http)
        result = await call_read(client, namespace, method, wrapper, asynchronous)
    assert result.rewards == rewards
    assert len(seen) == 1


@pytest.mark.parametrize("namespace,method,path,wrapper", READS)
@pytest.mark.parametrize("rewards", INVALID_REWARDS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_native_execution_reads_keep_response_validation(
    namespace, method, path, wrapper, rewards, asynchronous
):
    payload = reward_payload(path, wrapper, rewards)
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    ) as http:
        cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
        client = cls(harbor_api_version=SPEC["info"]["version"], httpx_client=http)
        with pytest.raises(ValidationError):
            await call_read(client, namespace, method, wrapper, asynchronous)


@pytest.mark.parametrize("namespace,method,path,wrapper", READS)
@pytest.mark.parametrize(
    "rewards", [{"accuracy": "1.0"}, {"accuracy": True}, {"accuracy": []}]
)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_checked_execution_reads_reject_non_numeric_wire_values(
    namespace, method, path, wrapper, rewards, asynchronous
):
    payload = reward_payload(path, wrapper, rewards)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    if asynchronous:
        async with async_client(transport=transport) as client:
            with pytest.raises(ContractError):
                await call_read(client, namespace, method, wrapper, asynchronous)
    else:
        with sync_client(transport=transport) as client:
            with pytest.raises(ContractError):
                await call_read(client, namespace, method, wrapper, asynchronous)


@pytest.mark.parametrize("value", [None, 0, -1, 0.5])
def test_exported_reward_value_alias_preserves_nullability(value):
    from typing import get_args

    from pydantic import TypeAdapter

    assert set(get_args(types.RewardValue)) == {float, type(None)}
    assert TypeAdapter(types.RewardValue).validate_python(value) == value


@pytest.mark.parametrize("value", ["invalid", {}, []])
def test_exported_reward_value_alias_rejects_invalid_values(value):
    from pydantic import TypeAdapter

    with pytest.raises(ValidationError):
        TypeAdapter(types.RewardValue).validate_python(value)
