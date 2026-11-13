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

TrialDetail1Phase = typing.Union[
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


class TrialDetail1(BaseModel):
    """TrialDetail1

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
    :type phase: TrialDetail1Phase
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
    :param lock: The persisted trial lock, or null for historical uploads without a lock.
    :type lock: Dict[str, Any]
    :param artifacts: Stored artifact paths by role; use the storage API to obtain authorized download URLs.
    :type artifacts: Dict[str, str]
    :param storage_error: Storage failures are not persisted in the trial resource.
    :type storage_error: Any
    :param result: Full result.json is available in the archived artifacts and is not reconstructed from partial database fields.
    :type result: Any
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
    phase: Optional[TrialDetail1Phase]
    task: TaskIdentity
    agent: AgentIdentity
    model: ModelIdentity
    rewards: Optional[Dict[str, Optional[float]]]
    usage: Usage
    error_type: Optional[str]
    lock: Optional[Dict[str, Any]] = Field(
        description="The persisted trial lock, or null for historical uploads without a lock."
    )
    artifacts: Dict[str, str] = Field(
        description="Stored artifact paths by role; use the storage API to obtain authorized download URLs."
    )
    storage_error: None = Field(
        description="Storage failures are not persisted in the trial resource."
    )
    result: None = Field(
        description="Full result.json is available in the archived artifacts and is not reconstructed from partial database fields."
    )
