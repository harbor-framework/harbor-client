from typing import Any, Optional, Generator, List, Union
from ..services.utils.validator import Validator
from ..services.utils.base_service import BaseService
from ..types.utils.sentinel import SENTINEL
from ..types.utils.cast_models import cast_models
from ..types.utils.base_model import construct_lenient
from ..types.rollouts_list_bad_request_response import (
    RolloutsListBadRequestResponse_adapter,
)
from ..types import (
    BadRequestEncoded,
    CancelRolloutsRequest,
    ConflictEncoded,
    FilterValuesResponse,
    ForbiddenEncoded,
    InternalServerErrorEncoded,
    NotFoundEncoded,
    RetryRolloutsRequest,
    RetryRolloutsResponse,
    RolloutActionRequest,
    RolloutResponse,
    RolloutsGetFiltersRequestField,
    RolloutsListBadRequestResponse,
    RolloutsListRequestSort,
    RunState,
    TrialActionResponse,
    TrialPage,
    TrialSummary,
    UnauthorizedEncoded,
)
from ..net.transport.serializer import Serializer
from ..net.transport.pagination import SyncPager
from ..net.transport.http_response import HttpResponse
from ..net.sdk_config import should_validate_response
from ..net.sdk_config import SdkConfig
from ..net.environment.environment import HarborAPIClientEnvironment
from ..core.request_options import RequestOptions
from ..services.async_.utils.to_async import to_async
from typing import Awaitable
from ..net.transport.pagination import AsyncPager
import asyncio


class RolloutsClient(BaseService):
    """
    Fern-style resource client for RolloutsClient.
    Exposes this resource's endpoints and, when the resource has sub-resources, lazy
    accessors to its child clients (`client.<parent>.<child>.method(...)`).
    Inherits authentication, base-url and request handling from BaseService.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the resource client, its child clients and method-level configs."""
        super().__init__(*args, **kwargs)
        self._raw_client = self.with_raw_response
        self._get_config: SdkConfig = {}
        self._list_config: SdkConfig = {}
        self._get_filters_config: SdkConfig = {}
        self._pause_config: SdkConfig = {}
        self._resume_config: SdkConfig = {}
        self._cancel_config: SdkConfig = {}
        self._retry_config: SdkConfig = {}

    def set_get_config(self, config: SdkConfig):
        """
        Sets method-level configuration for get.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._get_config = config
        return self

    def set_list_config(self, config: SdkConfig):
        """
        Sets method-level configuration for list.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._list_config = config
        return self

    def set_get_filters_config(self, config: SdkConfig):
        """
        Sets method-level configuration for get_filters.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._get_filters_config = config
        return self

    def set_pause_config(self, config: SdkConfig):
        """
        Sets method-level configuration for pause.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._pause_config = config
        return self

    def set_resume_config(self, config: SdkConfig):
        """
        Sets method-level configuration for resume.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._resume_config = config
        return self

    def set_cancel_config(self, config: SdkConfig):
        """
        Sets method-level configuration for cancel.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._cancel_config = config
        return self

    def set_retry_config(self, config: SdkConfig):
        """
        Sets method-level configuration for retry.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._retry_config = config
        return self

    @property
    def with_raw_response(self) -> "RawRolloutsClient":
        """
        Returns a raw-response client whose methods mirror this resource but return
        ``HttpResponse[T]`` (parsed body plus the raw status code and headers) instead of
        the bare deserialized body.
        """
        return RawRolloutsClient(self)

    @cast_models
    def get(
        self, rollout_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> RolloutResponse:
        """get

        :param rollout_id: rollout_id
        :type rollout_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: RolloutResponse
        """

        Validator(str).validate(rollout_id, "rollout_id")

        resolved_config = self._get_resolved_config(self._get_config, request_options)

        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts/{{rollout_id}}",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_path("rollout_id", rollout_id)
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("GET")
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                RolloutResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(RolloutResponse, response)
            )
        )

    @cast_models
    def list(
        self,
        *,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        page_size: str = SENTINEL,
        page_token: str = SENTINEL,
        sort: RolloutsListRequestSort = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPager[TrialSummary]:
        """list

        :param task: task, defaults to None
        :type task: List[str], optional
        :param state: state, defaults to None
        :type state: RunState, optional
        :param name: name, defaults to None
        :type name: str, optional
        :param q: q, defaults to None
        :type q: str, optional
        :param agent_name: agent_name, defaults to None
        :type agent_name: List[str], optional
        :param agent_version: agent_version, defaults to None
        :type agent_version: List[str], optional
        :param model_name: model_name, defaults to None
        :type model_name: List[str], optional
        :param model_provider: model_provider, defaults to None
        :type model_provider: List[str], optional
        :param reasoning_effort: reasoning_effort, defaults to None
        :type reasoning_effort: List[str], optional
        :param source: source, defaults to None
        :type source: List[str], optional
        :param created_after: created_after, defaults to None
        :type created_after: str, optional
        :param created_before: created_before, defaults to None
        :type created_before: str, optional
        :param job_id: job_id, defaults to None
        :type job_id: str, optional
        :param page_size: page_size, defaults to None
        :type page_size: str, optional
        :param page_token: page_token, defaults to None
        :type page_token: str, optional
        :param sort: sort, defaults to None
        :type sort: RolloutsListRequestSort, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: SyncPager[TrialSummary]
        """
        self = self._for_one_call()

        Validator(str).is_array().is_optional().validate(task, "task")
        Validator(RunState).is_optional().validate(state, "state")
        Validator(str).is_optional().validate(name, "name")
        Validator(str).is_optional().validate(q, "q")
        Validator(str).is_array().is_optional().validate(agent_name, "agent_name")
        Validator(str).is_array().is_optional().validate(agent_version, "agent_version")
        Validator(str).is_array().is_optional().validate(model_name, "model_name")
        Validator(str).is_array().is_optional().validate(
            model_provider, "model_provider"
        )
        Validator(str).is_array().is_optional().validate(
            reasoning_effort, "reasoning_effort"
        )
        Validator(str).is_array().is_optional().validate(source, "source")
        Validator(str).is_optional().validate(created_after, "created_after")
        Validator(str).is_optional().validate(created_before, "created_before")
        Validator(str).is_optional().validate(job_id, "job_id")
        Validator(str).is_optional().validate(page_size, "page_size")
        Validator(str).is_optional().validate(page_token, "page_token")
        Validator(RolloutsListRequestSort).is_optional().validate(sort, "sort")

        resolved_config = self._get_resolved_config(self._list_config, request_options)

        def _paginate() -> Generator[List[TrialSummary], None, None]:
            nonlocal page_token
            while True:
                serialized_request = (
                    Serializer(
                        f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts",
                        [self.get_access_token(resolved_config)],
                        resolved_config,
                    )
                    .add_header(
                        "Harbor-API-Version",
                        self._global_headers.get("Harbor-API-Version"),
                    )
                    .add_query("task", task)
                    .add_query("state", state)
                    .add_query("name", name)
                    .add_query("q", q)
                    .add_query("agent_name", agent_name)
                    .add_query("agent_version", agent_version)
                    .add_query("model_name", model_name)
                    .add_query("model_provider", model_provider)
                    .add_query("reasoning_effort", reasoning_effort)
                    .add_query("source", source)
                    .add_query("created_after", created_after)
                    .add_query("created_before", created_before)
                    .add_query("job_id", job_id)
                    .add_query("page_size", page_size)
                    .add_query("page_token", page_token)
                    .add_query("sort", sort)
                    .add_error(401, UnauthorizedEncoded)
                    .add_error(403, ForbiddenEncoded)
                    .add_error(404, NotFoundEncoded)
                    .add_error(500, InternalServerErrorEncoded)
                    .serialize()
                    .set_method("GET")
                )
                response, status, content = self.send_request(serialized_request)
                parsed_response = (
                    TrialPage.model_validate(response)
                    if should_validate_response(resolved_config)
                    else construct_lenient(TrialPage, response)
                )
                current_page = parsed_response.items

                yield current_page

                next_cursor = parsed_response.next_page_token
                if not next_cursor:
                    break

                page_token = next_cursor

        return SyncPager(_paginate(), lambda: self._last_response)

    @cast_models
    def get_filters(
        self,
        *,
        field: RolloutsGetFiltersRequestField,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        limit: str = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> FilterValuesResponse:
        """get_filters

        :param field: field
        :type field: RolloutsGetFiltersRequestField
        :param task: task, defaults to None
        :type task: List[str], optional
        :param state: state, defaults to None
        :type state: RunState, optional
        :param name: name, defaults to None
        :type name: str, optional
        :param q: q, defaults to None
        :type q: str, optional
        :param agent_name: agent_name, defaults to None
        :type agent_name: List[str], optional
        :param agent_version: agent_version, defaults to None
        :type agent_version: List[str], optional
        :param model_name: model_name, defaults to None
        :type model_name: List[str], optional
        :param model_provider: model_provider, defaults to None
        :type model_provider: List[str], optional
        :param reasoning_effort: reasoning_effort, defaults to None
        :type reasoning_effort: List[str], optional
        :param source: source, defaults to None
        :type source: List[str], optional
        :param created_after: created_after, defaults to None
        :type created_after: str, optional
        :param created_before: created_before, defaults to None
        :type created_before: str, optional
        :param job_id: job_id, defaults to None
        :type job_id: str, optional
        :param limit: limit, defaults to None
        :type limit: str, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: FilterValuesResponse
        """

        Validator(RolloutsGetFiltersRequestField).validate(field, "field")
        Validator(str).is_array().is_optional().validate(task, "task")
        Validator(RunState).is_optional().validate(state, "state")
        Validator(str).is_optional().validate(name, "name")
        Validator(str).is_optional().validate(q, "q")
        Validator(str).is_array().is_optional().validate(agent_name, "agent_name")
        Validator(str).is_array().is_optional().validate(agent_version, "agent_version")
        Validator(str).is_array().is_optional().validate(model_name, "model_name")
        Validator(str).is_array().is_optional().validate(
            model_provider, "model_provider"
        )
        Validator(str).is_array().is_optional().validate(
            reasoning_effort, "reasoning_effort"
        )
        Validator(str).is_array().is_optional().validate(source, "source")
        Validator(str).is_optional().validate(created_after, "created_after")
        Validator(str).is_optional().validate(created_before, "created_before")
        Validator(str).is_optional().validate(job_id, "job_id")
        Validator(str).is_optional().validate(limit, "limit")

        resolved_config = self._get_resolved_config(
            self._get_filters_config, request_options
        )

        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts/filters",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_query("task", task)
            .add_query("state", state)
            .add_query("name", name)
            .add_query("q", q)
            .add_query("agent_name", agent_name)
            .add_query("agent_version", agent_version)
            .add_query("model_name", model_name)
            .add_query("model_provider", model_provider)
            .add_query("reasoning_effort", reasoning_effort)
            .add_query("source", source)
            .add_query("created_after", created_after)
            .add_query("created_before", created_before)
            .add_query("job_id", job_id)
            .add_query("field", field)
            .add_query("limit", limit)
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("GET")
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                FilterValuesResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(FilterValuesResponse, response)
            )
        )

    @cast_models
    def pause(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> TrialActionResponse:
        """pause

        :param request_body: The request body.
        :type request_body: RolloutActionRequest
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialActionResponse
        """

        resolved_config = self._get_resolved_config(self._pause_config, request_options)

        request_body = RolloutActionRequest(rollout_ids=rollout_ids)
        Validator(RolloutActionRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts/pause",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                TrialActionResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(TrialActionResponse, response)
            )
        )

    @cast_models
    def resume(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> TrialActionResponse:
        """resume

        :param request_body: The request body.
        :type request_body: RolloutActionRequest
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialActionResponse
        """

        resolved_config = self._get_resolved_config(
            self._resume_config, request_options
        )

        request_body = RolloutActionRequest(rollout_ids=rollout_ids)
        Validator(RolloutActionRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts/resume",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                TrialActionResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(TrialActionResponse, response)
            )
        )

    @cast_models
    def cancel(
        self,
        *,
        rollout_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> TrialActionResponse:
        """Cancel the specified physical rollout attempts. force defaults to true; false lets running attempts finish. Terminal attempts are unchanged.

        :param request_body: The request body.
        :type request_body: CancelRolloutsRequest
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialActionResponse
        """

        resolved_config = self._get_resolved_config(
            self._cancel_config, request_options
        )

        request_body = CancelRolloutsRequest(
            rollout_ids=rollout_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
        )
        Validator(CancelRolloutsRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts/cancel",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                TrialActionResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(TrialActionResponse, response)
            )
        )

    @cast_models
    def retry(
        self,
        *,
        rollout_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> RetryRolloutsResponse:
        """Retry the specified latest terminal attempts. Idempotency-Key is required; replaying the same ordered selection returns the same new rollout IDs. Stale or active attempts return 409.

        :param request_body: The request body.
        :type request_body: RetryRolloutsRequest
        :param idempotency_key: idempotency_key
        :type idempotency_key: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: RetryRolloutsResponse
        """

        Validator(str).validate(idempotency_key, "idempotency_key")

        resolved_config = self._get_resolved_config(self._retry_config, request_options)

        request_body = RetryRolloutsRequest(rollout_ids=rollout_ids)
        Validator(RetryRolloutsRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/rollouts/retry",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_header("idempotency-key", idempotency_key)
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("POST")
            .set_body(request_body)
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                RetryRolloutsResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(RetryRolloutsResponse, response)
            )
        )


class RawRolloutsClient:
    """
    Raw-response client for RolloutsClient.

    Each method delegates to the matching :class:`RolloutsClient` method and wraps the result in
    an ``HttpResponse[T]`` so callers can read ``.data`` alongside ``.status_code`` and
    ``.headers``.
    """

    def __init__(self, client: RolloutsClient):
        self._client = client
        self._client_wrapper = client._client_wrapper

    def get(
        self, rollout_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[RolloutResponse]:
        data = RolloutsClient.get(
            self._client, rollout_id, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def list(
        self,
        *,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        page_size: str = SENTINEL,
        page_token: str = SENTINEL,
        sort: RolloutsListRequestSort = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[SyncPager[TrialSummary]]:
        data = RolloutsClient.list(
            self._client,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "task": task,
                        "state": state,
                        "name": name,
                        "q": q,
                        "agent_name": agent_name,
                        "agent_version": agent_version,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "reasoning_effort": reasoning_effort,
                        "source": source,
                        "created_after": created_after,
                        "created_before": created_before,
                        "job_id": job_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "sort": sort,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response_source=lambda: data.last_response)

    def get_filters(
        self,
        *,
        field: RolloutsGetFiltersRequestField,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        limit: str = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[FilterValuesResponse]:
        data = RolloutsClient.get_filters(
            self._client,
            field=field,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "task": task,
                        "state": state,
                        "name": name,
                        "q": q,
                        "agent_name": agent_name,
                        "agent_version": agent_version,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "reasoning_effort": reasoning_effort,
                        "source": source,
                        "created_after": created_after,
                        "created_before": created_before,
                        "job_id": job_id,
                        "limit": limit,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def pause(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = RolloutsClient.pause(
            self._client, rollout_ids=rollout_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def resume(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = RolloutsClient.resume(
            self._client, rollout_ids=rollout_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def cancel(
        self,
        *,
        rollout_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = RolloutsClient.cancel(
            self._client,
            rollout_ids=rollout_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def retry(
        self,
        *,
        rollout_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[RetryRolloutsResponse]:
        data = RolloutsClient.retry(
            self._client,
            rollout_ids=rollout_ids,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)


class AsyncRolloutsClient(RolloutsClient):
    """
    Async wrapper for RolloutsClient. Mirrors the sync client's endpoints (awaitable) and, for a
    resource with sub-resources, its lazy child accessors (returning the async child clients).
    """

    @property
    def with_raw_response(self) -> "AsyncRawRolloutsClient":  # type: ignore[override]
        """
        Returns an async raw-response client whose methods mirror this resource but return
        ``HttpResponse[T]`` (parsed body plus the raw status code and headers).
        """
        return AsyncRawRolloutsClient(self)

    def get(
        self, rollout_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> Awaitable[RolloutResponse]:  # type: ignore[override]
        return to_async(super().get)(rollout_id, request_options=request_options)

    def list(
        self,
        *,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        page_size: str = SENTINEL,
        page_token: str = SENTINEL,
        sort: RolloutsListRequestSort = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPager[TrialSummary]:  # type: ignore[override]
        sync_pager = super().list(
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "task": task,
                        "state": state,
                        "name": name,
                        "q": q,
                        "agent_name": agent_name,
                        "agent_version": agent_version,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "reasoning_effort": reasoning_effort,
                        "source": source,
                        "created_after": created_after,
                        "created_before": created_before,
                        "job_id": job_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "sort": sort,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )

        async def _paginate():
            pages = iter(sync_pager.iter_pages())
            while True:
                page = await to_async(next)(pages, None)
                if page is None:
                    break
                yield page

        return AsyncPager(_paginate(), lambda: sync_pager.last_response)

    def get_filters(
        self,
        *,
        field: RolloutsGetFiltersRequestField,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        limit: str = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[FilterValuesResponse]:  # type: ignore[override]
        return to_async(super().get_filters)(
            field=field,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "task": task,
                        "state": state,
                        "name": name,
                        "q": q,
                        "agent_name": agent_name,
                        "agent_version": agent_version,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "reasoning_effort": reasoning_effort,
                        "source": source,
                        "created_after": created_after,
                        "created_before": created_before,
                        "job_id": job_id,
                        "limit": limit,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )

    def pause(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[TrialActionResponse]:  # type: ignore[override]
        return to_async(super().pause)(
            rollout_ids=rollout_ids, request_options=request_options
        )

    def resume(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[TrialActionResponse]:  # type: ignore[override]
        return to_async(super().resume)(
            rollout_ids=rollout_ids, request_options=request_options
        )

    def cancel(
        self,
        *,
        rollout_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[TrialActionResponse]:  # type: ignore[override]
        return to_async(super().cancel)(
            rollout_ids=rollout_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
            request_options=request_options,
        )

    def retry(
        self,
        *,
        rollout_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[RetryRolloutsResponse]:  # type: ignore[override]
        return to_async(super().retry)(
            rollout_ids=rollout_ids,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )


class AsyncRawRolloutsClient:
    """
    Async raw-response client for AsyncRolloutsClient.
    """

    def __init__(self, client: AsyncRolloutsClient):
        self._client = client
        self._client_wrapper = client._client_wrapper

    async def get(
        self, rollout_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[RolloutResponse]:
        data = await AsyncRolloutsClient.get(
            self._client, rollout_id, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def list(
        self,
        *,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        page_size: str = SENTINEL,
        page_token: str = SENTINEL,
        sort: RolloutsListRequestSort = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[AsyncPager[TrialSummary]]:
        data = AsyncRolloutsClient.list(
            self._client,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "task": task,
                        "state": state,
                        "name": name,
                        "q": q,
                        "agent_name": agent_name,
                        "agent_version": agent_version,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "reasoning_effort": reasoning_effort,
                        "source": source,
                        "created_after": created_after,
                        "created_before": created_before,
                        "job_id": job_id,
                        "page_size": page_size,
                        "page_token": page_token,
                        "sort": sort,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response_source=lambda: data.last_response)

    async def get_filters(
        self,
        *,
        field: RolloutsGetFiltersRequestField,
        task: List[str] = SENTINEL,
        state: RunState = SENTINEL,
        name: str = SENTINEL,
        q: str = SENTINEL,
        agent_name: List[str] = SENTINEL,
        agent_version: List[str] = SENTINEL,
        model_name: List[str] = SENTINEL,
        model_provider: List[str] = SENTINEL,
        reasoning_effort: List[str] = SENTINEL,
        source: List[str] = SENTINEL,
        created_after: str = SENTINEL,
        created_before: str = SENTINEL,
        job_id: str = SENTINEL,
        limit: str = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[FilterValuesResponse]:
        data = await AsyncRolloutsClient.get_filters(
            self._client,
            field=field,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "task": task,
                        "state": state,
                        "name": name,
                        "q": q,
                        "agent_name": agent_name,
                        "agent_version": agent_version,
                        "model_name": model_name,
                        "model_provider": model_provider,
                        "reasoning_effort": reasoning_effort,
                        "source": source,
                        "created_after": created_after,
                        "created_before": created_before,
                        "job_id": job_id,
                        "limit": limit,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def pause(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = await AsyncRolloutsClient.pause(
            self._client, rollout_ids=rollout_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def resume(
        self,
        *,
        rollout_ids: List[str],
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = await AsyncRolloutsClient.resume(
            self._client, rollout_ids=rollout_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def cancel(
        self,
        *,
        rollout_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = await AsyncRolloutsClient.cancel(
            self._client,
            rollout_ids=rollout_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def retry(
        self,
        *,
        rollout_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[RetryRolloutsResponse]:
        data = await AsyncRolloutsClient.retry(
            self._client,
            rollout_ids=rollout_ids,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)
