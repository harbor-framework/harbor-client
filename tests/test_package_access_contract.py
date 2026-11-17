"""Package-access projections enforce the shared schema at the wire boundary."""

from copy import deepcopy

import httpx
import pytest

from harbor_client.validation import ContractError, async_client, sync_client
from test_contract import SPEC, UUID, example
from test_native_operations import arguments, snake

OPERATIONS = ["packages.getAccess", "packages.updateOrganizationAccess"]
COUNTS = [
    "newly_shared_task_count",
    "newly_unshared_task_count",
    "potentially_unavailable_third_party_task_count",
]
PRIVATE_MARKER = "private-input-not-for-error-messages"


def operation_info(operation_id):
    return next(
        (path, verb, operation)
        for path, methods in SPEC["paths"].items()
        for verb, operation in methods.items()
        if isinstance(operation, dict) and operation.get("operationId") == operation_id
    )


def projection(operation_id):
    _, _, operation = operation_info(operation_id)
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    payload = example(schema)
    payload["owner_organization"]["name"] = PRIVATE_MARKER
    payload["can_manage_access"] = False
    payload.pop("direct_public", None)
    payload.pop("public_grants", None)
    return payload


def grant(name):
    value = example(SPEC["components"]["schemas"][name])
    value["created_by"] = UUID
    value["created_by_user"] = example(
        SPEC["components"]["schemas"]["PackageAccessGrantCreator"]
    )
    return value


def full_projection(operation_id):
    payload = projection(operation_id)
    payload.update(
        direct_public=False,
        public_grants=[grant("PackagePublicGrant")],
        organization_grants=[grant("PackageOrganizationGrant")],
    )
    return payload


async def invoke(operation_id, payload, asynchronous):
    _, _, operation = operation_info(operation_id)
    _, name = operation_id.split(".")
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=payload))
    if asynchronous:
        async with async_client(transport=transport) as client:
            method = getattr(client.packages, snake(name))
            return await method(**arguments(operation, method))
    with sync_client(transport=transport) as client:
        method = getattr(client.packages, snake(name))
        return method(**arguments(operation, method))


@pytest.mark.parametrize("operation_id", OPERATIONS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("can_manage", [False, True])
@pytest.mark.parametrize("direct", ["missing", None, False, True])
@pytest.mark.parametrize("public", ["missing", None, []])
async def test_full_redacted_and_partial_provenance_combinations(
    operation_id, asynchronous, can_manage, direct, public
):
    payload = projection(operation_id)
    payload["can_manage_access"] = can_manage
    if direct != "missing":
        payload["direct_public"] = direct
    if public != "missing":
        payload["public_grants"] = public
    full = isinstance(direct, bool) and public == []
    redacted = not can_manage and direct == "missing" and public == "missing"
    if full or redacted:
        result = await invoke(operation_id, payload, asynchronous)
        assert result.can_manage_access is can_manage
        assert result.model_dump(mode="json", exclude_unset=True) == payload
    else:
        with pytest.raises(ContractError) as error:
            await invoke(operation_id, payload, asynchronous)
        assert PRIVATE_MARKER not in str(error.value)


@pytest.mark.parametrize("operation_id", OPERATIONS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_non_managing_callers_can_receive_typed_full_provenance(
    operation_id, asynchronous
):
    payload = full_projection(operation_id)
    result = await invoke(operation_id, payload, asynchronous)
    assert result.can_manage_access is False
    assert result.public_grants[0].source_package_id == UUID
    assert result.organization_grants[0].created_by_user.id == UUID
    assert result.model_dump(mode="json", exclude_unset=True) == payload


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("field", COUNTS)
async def test_negative_update_impact_counts_are_rejected(field, asynchronous):
    payload = full_projection("packages.updateOrganizationAccess")
    payload[field] = -1
    with pytest.raises(ContractError) as error:
        await invoke("packages.updateOrganizationAccess", payload, asynchronous)
    assert PRIVATE_MARKER not in str(error.value)
    assert "minimum" in str(error.value)


UUID_PATHS = [
    ("package_id",),
    ("owner_organization", "id"),
    ("organization_grants", 0, "source_package_id"),
    ("organization_grants", 0, "created_by"),
    ("organization_grants", 0, "created_by_user", "id"),
    ("organization_grants", 0, "recipient_organization", "id"),
    ("public_grants", 0, "source_package_id"),
    ("public_grants", 0, "created_by"),
    ("public_grants", 0, "created_by_user", "id"),
]


@pytest.mark.parametrize("operation_id", OPERATIONS)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("path", UUID_PATHS)
async def test_malformed_provenance_ids_fail_without_echoing_input(
    operation_id, asynchronous, path
):
    payload = deepcopy(full_projection(operation_id))
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = PRIVATE_MARKER
    with pytest.raises(ContractError) as error:
        await invoke(operation_id, payload, asynchronous)
    assert PRIVATE_MARKER not in str(error.value)
    assert PRIVATE_MARKER not in repr(error.value)
