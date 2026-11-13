from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from typing import Dict
from .utils.base_model import BaseModel
from .run_state import RunState
from .trial_counts import TrialCounts
from .mean_aggregate import MeanAggregate
from .usage_aggregates import UsageAggregates


class JobSummary(BaseModel):
    """JobSummary

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
    :param name: name
    :type name: str
    :param state: state
    :type state: RunState
    :param rollouts: rollouts
    :type rollouts: TrialCounts
    :param trials: trials, defaults to None
    :type trials: TrialCounts, optional
    :param n_retries: n_retries
    :type n_retries: int
    :param n_errors: n_errors
    :type n_errors: int
    :param agent_names: agent_names
    :type agent_names: List[str]
    :param model_names: model_names
    :type model_names: List[str]
    :param model_providers: model_providers
    :type model_providers: List[str]
    :param reasoning_efforts: reasoning_efforts
    :type reasoning_efforts: List[str]
    :param sources: sources
    :type sources: List[str]
    :param rewards: rewards
    :type rewards: Dict[str, MeanAggregate]
    :param usage: usage
    :type usage: UsageAggregates
    """

    created_at: str
    updated_at: str
    started_at: Optional[str]
    finished_at: Optional[str]
    id: str
    name: str
    state: RunState
    rollouts: TrialCounts
    trials: Optional[TrialCounts] = Field(default=None)
    n_retries: int
    n_errors: int
    agent_names: List[str]
    model_names: List[str]
    model_providers: List[str]
    reasoning_efforts: List[str]
    sources: List[str]
    rewards: Dict[str, MeanAggregate]
    usage: UsageAggregates

