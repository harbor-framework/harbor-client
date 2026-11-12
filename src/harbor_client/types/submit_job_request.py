from __future__ import annotations
import typing
from typing import Union
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Annotated
from pydantic import TypeAdapter
from typing import Dict
from .utils.base_model import BaseModel
from .hosted_diff_selectors import HostedDiffSelectors
from .hosted_agent_config import HostedAgentConfig
from .hosted_submission_environment_config import HostedSubmissionEnvironmentConfig
from .hosted_submission_task_config import HostedSubmissionTaskConfig
from .hosted_submission_dataset_config import HostedSubmissionDatasetConfig
from .hosted_submission_retry_config import HostedSubmissionRetryConfig
from .hosted_job_trial_regrade_source import HostedJobTrialRegradeSource


class SubmitJobRequest(BaseModel):
    """SubmitJobRequest

    :param config: config
    :type config: SubmitJobRequestConfig
    :param regrade: regrade, defaults to None
    :type regrade: SubmitJobRequestRegrade, optional
    :param organization_id: organization_id, defaults to None
    :type organization_id: str, optional
    :param job_secrets: job_secrets, defaults to None
    :type job_secrets: Dict[str, Any], optional
    :param job_credentials: job_credentials, defaults to None
    :type job_credentials: Dict[str, Any], optional
    :param registry_credentials: registry_credentials, defaults to None
    :type registry_credentials: Dict[str, Any], optional
    :param dry_run: dry_run, defaults to None
    :type dry_run: bool, optional
    """

    config: SubmitJobRequestConfig
    regrade: Optional[SubmitJobRequestRegrade] = Field(default=None)
    organization_id: Optional[str] = Field(default=None)
    job_secrets: Optional[Dict[str, Any]] = Field(default=None)
    job_credentials: Optional[Dict[str, Any]] = Field(default=None)
    registry_credentials: Optional[Dict[str, Any]] = Field(default=None)
    dry_run: Optional[bool] = Field(default=None)


SubmitJobRequestConfigCredentialMode = typing.Union[
    typing.Literal["gateway", "direct"], typing.Any
]


class SubmitJobRequestConfig(BaseModel):
    """SubmitJobRequestConfig

    :param diff: diff, defaults to None
    :type diff: HostedDiffSelectors, optional
    :param install_only: install_only, defaults to None
    :type install_only: bool, optional
    :param static_outbound_ip: static_outbound_ip, defaults to None
    :type static_outbound_ip: bool, optional
    :param credential_mode: credential_mode, defaults to None
    :type credential_mode: SubmitJobRequestConfigCredentialMode, optional
    :param agents: agents
    :type agents: List[HostedAgentConfig]
    :param environment: environment, defaults to None
    :type environment: HostedSubmissionEnvironmentConfig, optional
    :param tasks: tasks, defaults to None
    :type tasks: List[HostedSubmissionTaskConfig], optional
    :param datasets: datasets, defaults to None
    :type datasets: List[HostedSubmissionDatasetConfig], optional
    :param retry: retry, defaults to None
    :type retry: HostedSubmissionRetryConfig, optional
    :param n_attempts: n_attempts, defaults to None
    :type n_attempts: float, optional
    :param n_concurrent_trials: n_concurrent_trials, defaults to None
    :type n_concurrent_trials: float, optional
    """

    diff: Optional[HostedDiffSelectors] = Field(default=None)
    install_only: Optional[bool] = Field(default=None)
    static_outbound_ip: Optional[bool] = Field(default=None)
    credential_mode: Optional[SubmitJobRequestConfigCredentialMode] = Field(
        default=None
    )
    agents: List[HostedAgentConfig]
    environment: Optional[HostedSubmissionEnvironmentConfig] = Field(default=None)
    tasks: Optional[List[HostedSubmissionTaskConfig]] = Field(default=None)
    datasets: Optional[List[HostedSubmissionDatasetConfig]] = Field(default=None)
    retry: Optional[HostedSubmissionRetryConfig] = Field(default=None)
    n_attempts: Optional[float] = Field(default=None)
    n_concurrent_trials: Optional[float] = Field(default=None)


class SubmitJobRequestRegradeSourceTrialId(BaseModel):
    """SubmitJobRequestRegradeSourceTrialId

    :param source_trial_id: source_trial_id
    :type source_trial_id: str
    """

    source_trial_id: str


# Union type for SubmitJobRequestRegrade
# Pydantic will attempt to validate against each type in order
SubmitJobRequestRegrade = Union[
    SubmitJobRequestRegradeSourceTrialId, HostedJobTrialRegradeSource
]
# TypeAdapter for runtime validation of SubmitJobRequestRegrade
# This allows validation of Union types which are not directly instantiable

SubmitJobRequestRegrade_adapter = TypeAdapter(SubmitJobRequestRegrade)


# Rebuild model to resolve forward references from submodels
SubmitJobRequest.model_rebuild()
