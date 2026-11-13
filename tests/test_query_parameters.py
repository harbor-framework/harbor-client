"""Validate native repeated query filters without changing their wire encoding."""

import httpx
import pytest

from harbor_client.validation import (
    ContractError,
    ContractTransport,
    async_client,
    sync_client,
)
from test_contract import BASE, SPEC, response_fixture
from test_native_operations import arguments, snake

ARRAY_FILTERS = [
    (path, verb, operation, parameter)
    for path, methods in SPEC["paths"].items()
    for verb, operation in methods.items()
    if isinstance(operation, dict)
    for parameter in operation.get("parameters", [])
    if parameter.get("in") == "query"
    and parameter.get("schema", {}).get("type") == "array"
]
FILTER_IDS = [f"{case[2]['operationId']}-{case[3]['name']}" for case in ARRAY_FILTERS]


@pytest.mark.parametrize("path,verb,operation,parameter", ARRAY_FILTERS, ids=FILTER_IDS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("values", [["one"], ["a,b", "x/y + z?=%", "日本語"]])
async def test_native_array_filters_preserve_every_repeated_value(
    path, verb, operation, parameter, asynchronous, values
):
    payload = response_fixture(path, verb)
    seen = []

    def handler(request):
        seen.append(request)
        assert request.url.params.get_list(parameter["name"]) == values
        return httpx.Response(200, json=payload)

    namespace, name = operation["operationId"].split(".", 1)
    transport = httpx.MockTransport(handler)
    if asynchronous:
        async with async_client(transport=transport) as client:
            method = getattr(getattr(client, snake(namespace)), snake(name))
            kwargs = {**arguments(operation, method), snake(parameter["name"]): values}
            result = method(**kwargs)
            if "x-fern-pagination" in operation:
                await anext(result.iter_pages())
            else:
                await result
    else:
        with sync_client(transport=transport) as client:
            method = getattr(getattr(client, snake(namespace)), snake(name))
            kwargs = {**arguments(operation, method), snake(parameter["name"]): values}
            result = method(**kwargs)
            if "x-fern-pagination" in operation:
                next(result.iter_pages())
    assert len(seen) == 1


@pytest.mark.parametrize(
    "name,values",
    [
        ("q", ["one", "two"]),
        ("q", ["one", "one"]),
        ("page_size", ["10", "20"]),
        ("state", ["queued", "running"]),
    ],
)
def test_repeated_scalar_query_parameters_are_rejected_before_http(name, values):
    transport = ContractTransport(
        httpx.MockTransport(
            lambda request: pytest.fail("Repeated scalar reached the network")
        )
    )
    with httpx.Client(transport=transport) as client:
        with pytest.raises(ContractError):
            client.get(
                BASE + "/v1/jobs",
                params=[(name, value) for value in values],
                headers={"Harbor-API-Version": SPEC["info"]["version"]},
            )


def test_query_array_limits_are_still_enforced():
    transport = ContractTransport(
        httpx.MockTransport(
            lambda request: pytest.fail("Oversized array reached the network")
        )
    )
    with httpx.Client(transport=transport) as client:
        with pytest.raises(ContractError, match="maxItems"):
            client.get(
                BASE + "/v1/trials",
                params=[("model_name", "model")] * 101,
                headers={"Harbor-API-Version": SPEC["info"]["version"]},
            )
