from __future__ import annotations
import typing
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel

TaskEnvironmentRequirementPhase = typing.Union[
    typing.Literal["agent", "environment", "verifier"], typing.Any
]


class TaskEnvironmentRequirement(BaseModel):
    """TaskEnvironmentRequirement

    :param env_var: env_var
    :type env_var: str
    :param phase: phase
    :type phase: TaskEnvironmentRequirementPhase
    :param has_default: has_default
    :type has_default: bool
    """

    env_var: str
    phase: TaskEnvironmentRequirementPhase
    has_default: bool
