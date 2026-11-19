"""Trial and rollout aliases reuse one detail and page contract."""

from importlib.resources import files

import httpx
import pytest

from harbor_client import AsyncHarborAPIClient, HarborAPIClient, types
from test_contract import SPEC, UUID, example, response_fixture


def test_execution_aliases_reference_the_same_named_contracts():
    def response(path):
        return SPEC["paths"][path]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]

    assert (
        response("/v1/trials")
        == response("/v1/rollouts")
        == {"$ref": "#/components/schemas/TrialPage"}
    )
    assert (
        types.TrialResponse.model_fields["trial"].annotation
        is types.RolloutResponse.model_fields["rollout"].annotation
        is types.TrialDetail
    )
    assert not hasattr(types, "TrialDetail1")
    assert not hasattr(types, "TrialPage1")
    assert not files("harbor_client").joinpath("types/trial_detail1.py").is_file()
    assert not files("harbor_client").joinpath("types/trial_page1.py").is_file()
    assert "TrialDetail_1" not in SPEC["components"]["schemas"]
    assert "TrialPage_1" not in SPEC["components"]["schemas"]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_execution_aliases_parse_with_shared_detail_and_page_models(
    monkeypatch, asynchronous
):
    page_calls = []
    original = types.TrialPage.model_validate

    def validate(cls, value, *args, **kwargs):
        page_calls.append(value["items"][0]["name"])
        return original(value, *args, **kwargs)

    monkeypatch.setattr(types.TrialPage, "model_validate", classmethod(validate))

    def handler(request):
        resource = request.url.path.removeprefix("/functions/v1/api/v1/").split("/")[0]
        if request.url.path.endswith(UUID):
            payload = response_fixture(
                f"/v1/{resource}/{{{'trial_id' if resource == 'trials' else 'rollout_id'}}}"
            )
        else:
            payload = response_fixture(f"/v1/{resource}")
            item = example(
                SPEC["components"]["schemas"]["TrialSummary"], allow_null=False
            )
            item["name"] = resource
            payload.update(items=[item], total=1, next_page_token="")
        return httpx.Response(200, json=payload)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        cls = AsyncHarborAPIClient if asynchronous else HarborAPIClient
        client = cls(harbor_api_version=SPEC["info"]["version"], httpx_client=http)
        for resource in ["trials", "rollouts"]:
            service = getattr(client, resource)
            pager = service.list()
            page = (
                await anext(pager.iter_pages())
                if asynchronous
                else next(pager.iter_pages())
            )
            assert type(page[0]) is types.TrialSummary
            result = service.get(
                **{"trial_id" if resource == "trials" else "rollout_id": UUID}
            )
            if asynchronous:
                result = await result
            assert (
                type(getattr(result, "trial" if resource == "trials" else "rollout"))
                is types.TrialDetail
            )
    assert page_calls == ["trials", "rollouts"]
