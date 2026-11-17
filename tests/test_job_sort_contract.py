"""Job list sorting follows the selected API contract and generated literals."""

from typing import Literal, get_args, get_origin

import httpx
import pytest

from harbor_client.types.jobs_list_request_sort import JobsListRequestSort
from harbor_client.validation import ContractError, async_client, sync_client
from test_contract import SPEC, response_fixture


def test_retired_job_sort_values_are_absent_from_generated_literals():
    literals = {
        value
        for member in (JobsListRequestSort, *get_args(JobsListRequestSort))
        if get_origin(member) is Literal
        for value in get_args(member)
    }
    assert {"id", "-id", "created_at", "-created_at"} <= literals
    assert not {"updated_at", "-updated_at"} & literals
    parameter = next(
        item
        for item in SPEC["paths"]["/v1/jobs"]["get"]["parameters"]
        if item["name"] == "sort"
    )
    assert not {"updated_at", "-updated_at"} & set(
        parameter["schema"]["allOf"][0]["enum"]
    )


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "sort", ["id", "-id", "created_at", "-created_at", "updated_at", "-updated_at"]
)
async def test_job_sort_wire_contract(asynchronous, sort):
    payload = {**response_fixture("/v1/jobs"), "items": [], "next_page_token": ""}
    seen = []

    def handler(request):
        seen.append(request.url.params["sort"])
        return httpx.Response(200, json=payload)

    retired = sort in {"updated_at", "-updated_at"}
    transport = httpx.MockTransport(handler)
    if asynchronous:
        async with async_client(transport=transport) as client:
            if retired:
                with pytest.raises(ContractError):
                    await anext(client.jobs.list(sort=sort).iter_pages())
            else:
                assert await anext(client.jobs.list(sort=sort).iter_pages()) == []
    else:
        with sync_client(transport=transport) as client:
            if retired:
                with pytest.raises(ContractError):
                    next(client.jobs.list(sort=sort).iter_pages())
            else:
                assert next(client.jobs.list(sort=sort).iter_pages()) == []
    assert seen == ([] if retired else [sort])
