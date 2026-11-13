from typing import Any, Optional, Generator, List, Union
from ..services.utils.validator import Validator
from ..services.utils.base_service import BaseService
from ..types.utils.sentinel import SENTINEL
from ..types.utils.cast_models import cast_models
from ..types.utils.base_model import construct_lenient
from ..types.trials_list_bad_request_response import (
    TrialsListBadRequestResponse_adapter,
)
from ..types import (
    BadRequestEncoded,
    CancelTrialsRequest,
    ConflictEncoded,
    CreatedResultTrial,
    FilterValuesResponse,
    ForbiddenEncoded,
    InternalServerErrorEncoded,
    NotFoundEncoded,
    ResultModelUsage,
    ResultTrialCreate,
    ResultTrialCreateAgent,
    RetryTrialsRequest,
    RetryTrialsResponse,
    RunState,
    StorageCopyResult,
    StorageDownload,
    TooManyRequestsEncoded,
    TrialActionRequest,
    TrialActionResponse,
    TrialArtifactType,
    TrialPage,
    TrialResponse,
    TrialsCopyRequest,
    TrialsGetFiltersRequestField,
    TrialsListBadRequestResponse,
    TrialsListRequestSort,
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


class TrialsClient(BaseService):
    """
    Fern-style resource client for TrialsClient.
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
        self._create_config: SdkConfig = {}
        self._get_filters_config: SdkConfig = {}
        self._pause_config: SdkConfig = {}
        self._resume_config: SdkConfig = {}
        self._cancel_config: SdkConfig = {}
        self._retry_config: SdkConfig = {}
        self._get_artifact_download_config: SdkConfig = {}
        self._copy_config: SdkConfig = {}

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

    def set_create_config(self, config: SdkConfig):
        """
        Sets method-level configuration for create.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._create_config = config
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

    def set_get_artifact_download_config(self, config: SdkConfig):
        """
        Sets method-level configuration for get_artifact_download.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._get_artifact_download_config = config
        return self

    def set_copy_config(self, config: SdkConfig):
        """
        Sets method-level configuration for copy.

        :param SdkConfig config: Configuration dictionary to override service-level defaults.
        :return: The service instance for method chaining.
        """
        self._copy_config = config
        return self

    @property
    def with_raw_response(self) -> "RawTrialsClient":
        """
        Returns a raw-response client whose methods mirror this resource but return
        ``HttpResponse[T]`` (parsed body plus the raw status code and headers) instead of
        the bare deserialized body.
        """
        return RawTrialsClient(self)

    @cast_models
    def get(
        self, trial_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> TrialResponse:
        """get

        :param trial_id: trial_id
        :type trial_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialResponse
        """

        Validator(str).validate(trial_id, "trial_id")

        resolved_config = self._get_resolved_config(self._get_config, request_options)

        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/{{trial_id}}",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_path("trial_id", trial_id)
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
                TrialResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(TrialResponse, response)
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
        sort: TrialsListRequestSort = SENTINEL,
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
        :type sort: TrialsListRequestSort, optional
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: SyncPager[TrialSummary]
        """

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
        Validator(TrialsListRequestSort).is_optional().validate(sort, "sort")

        resolved_config = self._get_resolved_config(self._list_config, request_options)

        def _paginate() -> Generator[List[TrialSummary], None, None]:
            nonlocal page_token
            while True:
                serialized_request = (
                    Serializer(
                        f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials",
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

                if not current_page:
                    break

                yield current_page

                next_cursor = parsed_response.next_page_token
                if not next_cursor:
                    break

                page_token = next_cursor

        return SyncPager(_paginate(), lambda: self._last_response)

    @cast_models
    def create(
        self,
        *,
        trial_id: str,
        job_id: str,
        trial_name: str,
        task_name: str,
        task_content_hash: str,
        agent: ResultTrialCreateAgent,
        config: dict,
        lock: dict,
        started_at: Union[str, None] = SENTINEL,
        finished_at: Union[str, None] = SENTINEL,
        rewards: Union[dict, None] = SENTINEL,
        exception_type: Union[str, None] = SENTINEL,
        models: List[ResultModelUsage] = SENTINEL,
        environment_setup_started_at: Union[str, None] = SENTINEL,
        environment_setup_finished_at: Union[str, None] = SENTINEL,
        agent_setup_started_at: Union[str, None] = SENTINEL,
        agent_setup_finished_at: Union[str, None] = SENTINEL,
        agent_execution_started_at: Union[str, None] = SENTINEL,
        agent_execution_finished_at: Union[str, None] = SENTINEL,
        verifier_started_at: Union[str, None] = SENTINEL,
        verifier_finished_at: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> CreatedResultTrial:
        """create

        :param request_body: The request body.
        :type request_body: ResultTrialCreate
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: CreatedResultTrial
        """

        resolved_config = self._get_resolved_config(
            self._create_config, request_options
        )

        request_body = ResultTrialCreate(
            trial_id=trial_id,
            job_id=job_id,
            trial_name=trial_name,
            task_name=task_name,
            task_content_hash=task_content_hash,
            agent=agent,
            config=config,
            lock=lock,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "rewards": rewards,
                        "exception_type": exception_type,
                        "models": models,
                        "environment_setup_started_at": environment_setup_started_at,
                        "environment_setup_finished_at": environment_setup_finished_at,
                        "agent_setup_started_at": agent_setup_started_at,
                        "agent_setup_finished_at": agent_setup_finished_at,
                        "agent_execution_started_at": agent_execution_started_at,
                        "agent_execution_finished_at": agent_execution_finished_at,
                        "verifier_started_at": verifier_started_at,
                        "verifier_finished_at": verifier_finished_at,
                    }.items()
                    if v is not SENTINEL
                }
            ),
        )
        Validator(ResultTrialCreate).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials",
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
                CreatedResultTrial.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(CreatedResultTrial, response)
            )
        )

    @cast_models
    def get_filters(
        self,
        *,
        field: TrialsGetFiltersRequestField,
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
        :type field: TrialsGetFiltersRequestField
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

        Validator(TrialsGetFiltersRequestField).validate(field, "field")
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
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/filters",
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
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> TrialActionResponse:
        """pause

        :param request_body: The request body.
        :type request_body: TrialActionRequest
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialActionResponse
        """

        resolved_config = self._get_resolved_config(self._pause_config, request_options)

        request_body = TrialActionRequest(trial_ids=trial_ids)
        Validator(TrialActionRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/pause",
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
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> TrialActionResponse:
        """resume

        :param request_body: The request body.
        :type request_body: TrialActionRequest
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialActionResponse
        """

        resolved_config = self._get_resolved_config(
            self._resume_config, request_options
        )

        request_body = TrialActionRequest(trial_ids=trial_ids)
        Validator(TrialActionRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/resume",
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
        trial_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> TrialActionResponse:
        """Cancel the specified physical trial attempts. force defaults to true; false lets running attempts finish. Terminal attempts are unchanged.

        :param request_body: The request body.
        :type request_body: CancelTrialsRequest
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: TrialActionResponse
        """

        resolved_config = self._get_resolved_config(
            self._cancel_config, request_options
        )

        request_body = CancelTrialsRequest(
            trial_ids=trial_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
        )
        Validator(CancelTrialsRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/cancel",
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
        trial_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> RetryTrialsResponse:
        """Retry the specified latest terminal attempts. Idempotency-Key is required; replaying the same ordered selection returns the same new trial IDs. Stale or active attempts return 409.

        :param request_body: The request body.
        :type request_body: RetryTrialsRequest
        :param idempotency_key: idempotency_key
        :type idempotency_key: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: RetryTrialsResponse
        """

        Validator(str).validate(idempotency_key, "idempotency_key")

        resolved_config = self._get_resolved_config(self._retry_config, request_options)

        request_body = RetryTrialsRequest(trial_ids=trial_ids)
        Validator(RetryTrialsRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/retry",
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
                RetryTrialsResponse.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(RetryTrialsResponse, response)
            )
        )

    @cast_models
    def get_artifact_download(
        self,
        trial_id: str,
        *,
        artifact_type: TrialArtifactType,
        request_options: Optional[RequestOptions] = None,
    ) -> StorageDownload:
        """get_artifact_download

        :param trial_id: trial_id
        :type trial_id: str
        :param artifact_type: artifact_type
        :type artifact_type: TrialArtifactType
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: StorageDownload
        """

        Validator(str).validate(trial_id, "trial_id")
        Validator(TrialArtifactType).validate(artifact_type, "artifact_type")

        resolved_config = self._get_resolved_config(
            self._get_artifact_download_config, request_options
        )

        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/{{trial_id}}/artifacts",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_path("trial_id", trial_id)
            .add_query("artifact_type", artifact_type)
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(429, TooManyRequestsEncoded)
            .add_error(500, InternalServerErrorEncoded)
            .serialize()
            .set_method("GET")
        )

        response, status, content = self.send_request(serialized_request)
        return (
            None
            if response in (b"", "")
            else (
                StorageDownload.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(StorageDownload, response)
            )
        )

    @cast_models
    def copy(
        self,
        source_trial_id: str,
        *,
        new_name: Union[str, None] = SENTINEL,
        overwrite: Union[bool, None] = SENTINEL,
        target_organization_id: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> StorageCopyResult:
        """copy

        :param request_body: The request body.
        :type request_body: TrialsCopyRequest
        :param source_trial_id: source_trial_id
        :type source_trial_id: str
        ...
        :raises RequestError: Raised when a request fails, with optional HTTP status code and details.
        ...
        :return: The parsed response data.
        :rtype: StorageCopyResult
        """

        Validator(str).validate(source_trial_id, "source_trial_id")

        resolved_config = self._get_resolved_config(self._copy_config, request_options)

        request_body = TrialsCopyRequest(
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "new_name": new_name,
                        "overwrite": overwrite,
                        "target_organization_id": target_organization_id,
                    }.items()
                    if v is not SENTINEL
                }
            )
        )
        Validator(TrialsCopyRequest).validate(request_body, "request_body")
        serialized_request = (
            Serializer(
                f"{self._resolve_base_url(resolved_config) or HarborAPIClientEnvironment.DEFAULT.url}/v1/trials/{{source_trial_id}}/copy",
                [self.get_access_token(resolved_config)],
                resolved_config,
            )
            .add_header(
                "Harbor-API-Version", self._global_headers.get("Harbor-API-Version")
            )
            .add_path("source_trial_id", source_trial_id)
            .add_error(401, UnauthorizedEncoded)
            .add_error(403, ForbiddenEncoded)
            .add_error(404, NotFoundEncoded)
            .add_error(429, TooManyRequestsEncoded)
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
                StorageCopyResult.model_validate(response)
                if should_validate_response(resolved_config)
                else construct_lenient(StorageCopyResult, response)
            )
        )


class RawTrialsClient:
    """
    Raw-response client for TrialsClient.

    Each method delegates to the matching :class:`TrialsClient` method and wraps the result in
    an ``HttpResponse[T]`` so callers can read ``.data`` alongside ``.status_code`` and
    ``.headers``.
    """

    def __init__(self, client: TrialsClient):
        self._client = client
        self._client_wrapper = client._client_wrapper

    def get(
        self, trial_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[TrialResponse]:
        data = TrialsClient.get(self._client, trial_id, request_options=request_options)
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
        sort: TrialsListRequestSort = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[SyncPager[TrialSummary]]:
        data = TrialsClient.list(
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

    def create(
        self,
        *,
        trial_id: str,
        job_id: str,
        trial_name: str,
        task_name: str,
        task_content_hash: str,
        agent: ResultTrialCreateAgent,
        config: dict,
        lock: dict,
        started_at: Union[str, None] = SENTINEL,
        finished_at: Union[str, None] = SENTINEL,
        rewards: Union[dict, None] = SENTINEL,
        exception_type: Union[str, None] = SENTINEL,
        models: List[ResultModelUsage] = SENTINEL,
        environment_setup_started_at: Union[str, None] = SENTINEL,
        environment_setup_finished_at: Union[str, None] = SENTINEL,
        agent_setup_started_at: Union[str, None] = SENTINEL,
        agent_setup_finished_at: Union[str, None] = SENTINEL,
        agent_execution_started_at: Union[str, None] = SENTINEL,
        agent_execution_finished_at: Union[str, None] = SENTINEL,
        verifier_started_at: Union[str, None] = SENTINEL,
        verifier_finished_at: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[CreatedResultTrial]:
        data = TrialsClient.create(
            self._client,
            trial_id=trial_id,
            job_id=job_id,
            trial_name=trial_name,
            task_name=task_name,
            task_content_hash=task_content_hash,
            agent=agent,
            config=config,
            lock=lock,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "rewards": rewards,
                        "exception_type": exception_type,
                        "models": models,
                        "environment_setup_started_at": environment_setup_started_at,
                        "environment_setup_finished_at": environment_setup_finished_at,
                        "agent_setup_started_at": agent_setup_started_at,
                        "agent_setup_finished_at": agent_setup_finished_at,
                        "agent_execution_started_at": agent_execution_started_at,
                        "agent_execution_finished_at": agent_execution_finished_at,
                        "verifier_started_at": verifier_started_at,
                        "verifier_finished_at": verifier_finished_at,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def get_filters(
        self,
        *,
        field: TrialsGetFiltersRequestField,
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
        data = TrialsClient.get_filters(
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
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[TrialActionResponse]:
        data = TrialsClient.pause(
            self._client, trial_ids=trial_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def resume(
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[TrialActionResponse]:
        data = TrialsClient.resume(
            self._client, trial_ids=trial_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def cancel(
        self,
        *,
        trial_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = TrialsClient.cancel(
            self._client,
            trial_ids=trial_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def retry(
        self,
        *,
        trial_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[RetryTrialsResponse]:
        data = TrialsClient.retry(
            self._client,
            trial_ids=trial_ids,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def get_artifact_download(
        self,
        trial_id: str,
        *,
        artifact_type: TrialArtifactType,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[StorageDownload]:
        data = TrialsClient.get_artifact_download(
            self._client,
            trial_id,
            artifact_type=artifact_type,
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    def copy(
        self,
        source_trial_id: str,
        *,
        new_name: Union[str, None] = SENTINEL,
        overwrite: Union[bool, None] = SENTINEL,
        target_organization_id: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[StorageCopyResult]:
        data = TrialsClient.copy(
            self._client,
            source_trial_id,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "new_name": new_name,
                        "overwrite": overwrite,
                        "target_organization_id": target_organization_id,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)


class AsyncTrialsClient(TrialsClient):
    """
    Async wrapper for TrialsClient. Mirrors the sync client's endpoints (awaitable) and, for a
    resource with sub-resources, its lazy child accessors (returning the async child clients).
    """

    @property
    def with_raw_response(self) -> "AsyncRawTrialsClient":  # type: ignore[override]
        """
        Returns an async raw-response client whose methods mirror this resource but return
        ``HttpResponse[T]`` (parsed body plus the raw status code and headers).
        """
        return AsyncRawTrialsClient(self)

    def get(
        self, trial_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> Awaitable[TrialResponse]:  # type: ignore[override]
        return to_async(super().get)(trial_id, request_options=request_options)

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
        sort: TrialsListRequestSort = SENTINEL,
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
            for page in sync_pager.iter_pages():
                yield page

        return AsyncPager(_paginate(), lambda: sync_pager.last_response)

    def create(
        self,
        *,
        trial_id: str,
        job_id: str,
        trial_name: str,
        task_name: str,
        task_content_hash: str,
        agent: ResultTrialCreateAgent,
        config: dict,
        lock: dict,
        started_at: Union[str, None] = SENTINEL,
        finished_at: Union[str, None] = SENTINEL,
        rewards: Union[dict, None] = SENTINEL,
        exception_type: Union[str, None] = SENTINEL,
        models: List[ResultModelUsage] = SENTINEL,
        environment_setup_started_at: Union[str, None] = SENTINEL,
        environment_setup_finished_at: Union[str, None] = SENTINEL,
        agent_setup_started_at: Union[str, None] = SENTINEL,
        agent_setup_finished_at: Union[str, None] = SENTINEL,
        agent_execution_started_at: Union[str, None] = SENTINEL,
        agent_execution_finished_at: Union[str, None] = SENTINEL,
        verifier_started_at: Union[str, None] = SENTINEL,
        verifier_finished_at: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[CreatedResultTrial]:  # type: ignore[override]
        return to_async(super().create)(
            trial_id=trial_id,
            job_id=job_id,
            trial_name=trial_name,
            task_name=task_name,
            task_content_hash=task_content_hash,
            agent=agent,
            config=config,
            lock=lock,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "rewards": rewards,
                        "exception_type": exception_type,
                        "models": models,
                        "environment_setup_started_at": environment_setup_started_at,
                        "environment_setup_finished_at": environment_setup_finished_at,
                        "agent_setup_started_at": agent_setup_started_at,
                        "agent_setup_finished_at": agent_setup_finished_at,
                        "agent_execution_started_at": agent_execution_started_at,
                        "agent_execution_finished_at": agent_execution_finished_at,
                        "verifier_started_at": verifier_started_at,
                        "verifier_finished_at": verifier_finished_at,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )

    def get_filters(
        self,
        *,
        field: TrialsGetFiltersRequestField,
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
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> Awaitable[TrialActionResponse]:  # type: ignore[override]
        return to_async(super().pause)(
            trial_ids=trial_ids, request_options=request_options
        )

    def resume(
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> Awaitable[TrialActionResponse]:  # type: ignore[override]
        return to_async(super().resume)(
            trial_ids=trial_ids, request_options=request_options
        )

    def cancel(
        self,
        *,
        trial_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[TrialActionResponse]:  # type: ignore[override]
        return to_async(super().cancel)(
            trial_ids=trial_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
            request_options=request_options,
        )

    def retry(
        self,
        *,
        trial_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[RetryTrialsResponse]:  # type: ignore[override]
        return to_async(super().retry)(
            trial_ids=trial_ids,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )

    def get_artifact_download(
        self,
        trial_id: str,
        *,
        artifact_type: TrialArtifactType,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[StorageDownload]:  # type: ignore[override]
        return to_async(super().get_artifact_download)(
            trial_id, artifact_type=artifact_type, request_options=request_options
        )

    def copy(
        self,
        source_trial_id: str,
        *,
        new_name: Union[str, None] = SENTINEL,
        overwrite: Union[bool, None] = SENTINEL,
        target_organization_id: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> Awaitable[StorageCopyResult]:  # type: ignore[override]
        return to_async(super().copy)(
            source_trial_id,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "new_name": new_name,
                        "overwrite": overwrite,
                        "target_organization_id": target_organization_id,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )


class AsyncRawTrialsClient:
    """
    Async raw-response client for AsyncTrialsClient.
    """

    def __init__(self, client: AsyncTrialsClient):
        self._client = client
        self._client_wrapper = client._client_wrapper

    async def get(
        self, trial_id: str, *, request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[TrialResponse]:
        data = await AsyncTrialsClient.get(
            self._client, trial_id, request_options=request_options
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
        sort: TrialsListRequestSort = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[AsyncPager[TrialSummary]]:
        data = AsyncTrialsClient.list(
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

    async def create(
        self,
        *,
        trial_id: str,
        job_id: str,
        trial_name: str,
        task_name: str,
        task_content_hash: str,
        agent: ResultTrialCreateAgent,
        config: dict,
        lock: dict,
        started_at: Union[str, None] = SENTINEL,
        finished_at: Union[str, None] = SENTINEL,
        rewards: Union[dict, None] = SENTINEL,
        exception_type: Union[str, None] = SENTINEL,
        models: List[ResultModelUsage] = SENTINEL,
        environment_setup_started_at: Union[str, None] = SENTINEL,
        environment_setup_finished_at: Union[str, None] = SENTINEL,
        agent_setup_started_at: Union[str, None] = SENTINEL,
        agent_setup_finished_at: Union[str, None] = SENTINEL,
        agent_execution_started_at: Union[str, None] = SENTINEL,
        agent_execution_finished_at: Union[str, None] = SENTINEL,
        verifier_started_at: Union[str, None] = SENTINEL,
        verifier_finished_at: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[CreatedResultTrial]:
        data = await AsyncTrialsClient.create(
            self._client,
            trial_id=trial_id,
            job_id=job_id,
            trial_name=trial_name,
            task_name=task_name,
            task_content_hash=task_content_hash,
            agent=agent,
            config=config,
            lock=lock,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "rewards": rewards,
                        "exception_type": exception_type,
                        "models": models,
                        "environment_setup_started_at": environment_setup_started_at,
                        "environment_setup_finished_at": environment_setup_finished_at,
                        "agent_setup_started_at": agent_setup_started_at,
                        "agent_setup_finished_at": agent_setup_finished_at,
                        "agent_execution_started_at": agent_execution_started_at,
                        "agent_execution_finished_at": agent_execution_finished_at,
                        "verifier_started_at": verifier_started_at,
                        "verifier_finished_at": verifier_finished_at,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def get_filters(
        self,
        *,
        field: TrialsGetFiltersRequestField,
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
        data = await AsyncTrialsClient.get_filters(
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
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[TrialActionResponse]:
        data = await AsyncTrialsClient.pause(
            self._client, trial_ids=trial_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def resume(
        self, *, trial_ids: List[str], request_options: Optional[RequestOptions] = None
    ) -> HttpResponse[TrialActionResponse]:
        data = await AsyncTrialsClient.resume(
            self._client, trial_ids=trial_ids, request_options=request_options
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def cancel(
        self,
        *,
        trial_ids: List[str],
        force: bool = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[TrialActionResponse]:
        data = await AsyncTrialsClient.cancel(
            self._client,
            trial_ids=trial_ids,
            **dict[str, Any](
                {k: v for k, v in {"force": force}.items() if v is not SENTINEL}
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def retry(
        self,
        *,
        trial_ids: List[str],
        idempotency_key: str,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[RetryTrialsResponse]:
        data = await AsyncTrialsClient.retry(
            self._client,
            trial_ids=trial_ids,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def get_artifact_download(
        self,
        trial_id: str,
        *,
        artifact_type: TrialArtifactType,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[StorageDownload]:
        data = await AsyncTrialsClient.get_artifact_download(
            self._client,
            trial_id,
            artifact_type=artifact_type,
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)

    async def copy(
        self,
        source_trial_id: str,
        *,
        new_name: Union[str, None] = SENTINEL,
        overwrite: Union[bool, None] = SENTINEL,
        target_organization_id: Union[str, None] = SENTINEL,
        request_options: Optional[RequestOptions] = None,
    ) -> HttpResponse[StorageCopyResult]:
        data = await AsyncTrialsClient.copy(
            self._client,
            source_trial_id,
            **dict[str, Any](
                {
                    k: v
                    for k, v in {
                        "new_name": new_name,
                        "overwrite": overwrite,
                        "target_organization_id": target_organization_id,
                    }.items()
                    if v is not SENTINEL
                }
            ),
            request_options=request_options,
        )
        return HttpResponse(data=data, response=self._client._last_response)
