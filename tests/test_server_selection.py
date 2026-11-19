"""Native trial selection stays in query parameters through cursor pagination."""

import httpx
import pytest

from harbor_client.validation import async_client, sync_client
from test_contract import SPEC, UUID, example, response_fixture

JOB_IDS = [UUID, UUID[:-1] + "2"]


async def invoke(namespace, method, arguments, handler, asynchronous):
    transport = httpx.MockTransport(handler)
    if asynchronous:
        async with async_client(transport=transport) as client:
            result = getattr(getattr(client, namespace), method)(**arguments)
            if method == "list":
                return [item async for item in result]
            return await result
    with sync_client(transport=transport) as client:
        result = getattr(getattr(client, namespace), method)(**arguments)
        return list(result) if method == "list" else result


@pytest.mark.parametrize("namespace", ["trials", "rollouts"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("attempts", ["all", "latest"])
async def test_server_filters_survive_empty_pages_and_opaque_cursors(
    namespace, asynchronous, attempts
):
    page = response_fixture(f"/v1/{namespace}")
    item = example(SPEC["components"]["schemas"]["TrialSummary"])
    item.update(job_id=UUID, state="finished", error_type="RuntimeError")
    cursor = "opaque+/=next?%20"
    seen = []

    def handler(request):
        query = request.url.params
        assert query.get_list("job_ids") == JOB_IDS
        assert query["job_id"] == UUID
        assert query["attempts"] == attempts
        assert query.get_list("error_type") == ["RuntimeError", "TimeoutError"]
        assert query["failed_only"] == "true"
        assert query["terminal"] == "true"
        assert query["sort"] == "-error_type"
        seen.append(query.get("page_token"))
        if len(seen) == 1:
            return httpx.Response(
                200, json={**page, "items": [], "next_page_token": cursor}
            )
        return httpx.Response(
            200, json={**page, "items": [item], "next_page_token": ""}
        )

    results = await invoke(
        namespace,
        "list",
        {
            "job_ids": JOB_IDS,
            "job_id": UUID,
            "attempts": attempts,
            "error_type": ["RuntimeError", "TimeoutError"],
            "failed_only": "true",
            "terminal": "true",
            "sort": "-error_type",
        },
        handler,
        asynchronous,
    )
    assert seen == [None, cursor]
    assert [result.id for result in results] == [item["id"]]


@pytest.mark.parametrize("namespace", ["trials", "rollouts"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("sort", ["error_type", "-error_type"])
async def test_nullable_error_type_rows_decode_with_both_sort_directions(
    namespace, asynchronous, sort
):
    page = response_fixture(f"/v1/{namespace}")
    item = example(SPEC["components"]["schemas"]["TrialSummary"])
    item["error_type"] = None

    def handler(request):
        assert request.url.params["sort"] == sort
        return httpx.Response(
            200, json={**page, "items": [item], "next_page_token": ""}
        )

    results = await invoke(namespace, "list", {"sort": sort}, handler, asynchronous)
    assert len(results) == 1
    assert results[0].error_type is None


@pytest.mark.parametrize("namespace", ["trials", "rollouts"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("flag", ["true", "false"])
async def test_facets_use_server_selection_and_return_typed_counts(
    namespace, asynchronous, flag
):
    payload = {
        "field": "error_type",
        "values": [{"value": "RuntimeError", "count": 3}],
        "truncated": True,
    }

    def handler(request):
        query = request.url.params
        assert query.get_list("job_ids") == JOB_IDS
        assert query["attempts"] == "latest"
        assert query.get_list("error_type") == ["RuntimeError"]
        assert query["failed_only"] == flag
        assert query["terminal"] == flag
        assert query["field"] == "error_type"
        return httpx.Response(200, json=payload)

    result = await invoke(
        namespace,
        "get_filters",
        {
            "field": "error_type",
            "job_ids": JOB_IDS,
            "attempts": "latest",
            "error_type": ["RuntimeError"],
            "failed_only": flag,
            "terminal": flag,
        },
        handler,
        asynchronous,
    )
    assert type(result).__name__ == "TrialFilterValuesResponse"
    assert result.values[0].value == "RuntimeError"
    assert result.values[0].count == 3
    assert result.model_dump(mode="json", exclude_unset=True) == payload


@pytest.mark.parametrize("namespace", ["trials", "rollouts"])
@pytest.mark.parametrize("method", ["list", "get_filters"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "invalid",
    [
        {"job_ids": ["invalid-uuid"]},
        {"job_ids": [UUID] * 101},
        {"attempts": "first"},
        {"failed_only": "yes"},
        {"terminal": "yes"},
    ],
)
async def test_invalid_server_filter_values_fail_before_http(
    namespace, method, asynchronous, invalid
):
    arguments = {"field": "error_type"} if method == "get_filters" else {}
    with pytest.raises((ValueError, TypeError)):
        await invoke(
            namespace,
            method,
            {**arguments, **invalid},
            lambda request: pytest.fail("Invalid server filter reached HTTP"),
            asynchronous,
        )
