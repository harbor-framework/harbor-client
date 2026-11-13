from __future__ import annotations
import typing
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from typing import Dict
from .utils.base_model import BaseModel
from .run_state import RunState
from .task_identity import TaskIdentity
from .agent_identity import AgentIdentity
from .model_identity import ModelIdentity
from .usage import Usage

TrialSummaryPhase = typing.Union[
    typing.Literal[
        "environment_setup",
        "agent_setup",
        "agent_execution",
        "verifier",
        "collection",
        "cleanup",
    ],
    typing.Any,
]


class TrialSummary(BaseModel):
    """TrialSummary

    :param created_at: created_at
    :type created_at: str
    :param updated_at: updated_at
    :type updated_at: str
    :param started_at: started_at
    :type started_at: str
    :param finished_at: finished_at
    :type finished_at: str
    :param id: id
    :type id: str
    :param job_id: job_id
    :type job_id: str
    :param name: name
    :type name: str
    :param state: state
    :type state: RunState
    :param retry_ids: All readable attempts of this logical trial, newest first, including this attempt.
    :type retry_ids: List[str]
    :param phase: phase
    :type phase: TrialSummaryPhase
    :param task: task
    :type task: TaskIdentity
    :param agent: agent
    :type agent: AgentIdentity
    :param model: model
    :type model: ModelIdentity
    :param rewards: rewards
    :type rewards: Dict[str, Optional[float]]
    :param usage: usage
    :type usage: Usage
    :param error_type: error_type
    :type error_type: str
    """

    created_at: str
    updated_at: str
    started_at: Optional[str]
    finished_at: Optional[str]
    id: str
    job_id: str
    name: str
    state: RunState
    retry_ids: List[str] = Field(
        description="All readable attempts of this logical trial, newest first, including this attempt."
    )
    phase: Optional[TrialSummaryPhase]
    task: TaskIdentity
    agent: AgentIdentity
    model: ModelIdentity
    rewards: Optional[Dict[str, Optional[float]]]
    usage: Usage
    error_type: Optional[str]
