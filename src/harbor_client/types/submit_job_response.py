from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from typing import Dict
from .utils.base_model import BaseModel
from .owner_organization import OwnerOrganization
from .selected_secret import SelectedSecret
from .agent_source import AgentSource


class SubmitJobResponse(BaseModel):
    """SubmitJobResponse

    :param job_id: job_id
    :type job_id: str
    :param job_name: job_name, defaults to None
    :type job_name: str, optional
    :param viewer_url: viewer_url, defaults to None
    :type viewer_url: str, optional
    :param status_url: status_url, defaults to None
    :type status_url: str, optional
    :param n_trials: n_trials, defaults to None
    :type n_trials: int, optional
    :param config: config, defaults to None
    :type config: Dict[str, Any], optional
    :param owner_organization: owner_organization, defaults to None
    :type owner_organization: OwnerOrganization, optional
    :param warnings: warnings, defaults to None
    :type warnings: List[str], optional
    :param selected_secrets: selected_secrets, defaults to None
    :type selected_secrets: List[SelectedSecret], optional
    :param agent_sources: agent_sources, defaults to None
    :type agent_sources: List[AgentSource], optional
    :param session_id: session_id, defaults to None
    :type session_id: str, optional
    """

    job_id: str
    job_name: Optional[str] = Field(default=None)
    viewer_url: Optional[str] = Field(default=None)
    status_url: Optional[str] = Field(default=None)
    n_trials: Optional[int] = Field(default=None)
    config: Optional[Dict[str, Any]] = Field(default=None)
    owner_organization: Optional[OwnerOrganization] = Field(default=None)
    warnings: Optional[List[str]] = Field(default=None)
    selected_secrets: Optional[List[SelectedSecret]] = Field(default=None)
    agent_sources: Optional[List[AgentSource]] = Field(default=None)
    session_id: Optional[str] = Field(default=None)
