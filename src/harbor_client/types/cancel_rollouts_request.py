from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class CancelRolloutsRequest(BaseModel):
    """CancelRolloutsRequest

    :param rollout_ids: rollout_ids
    :type rollout_ids: List[str]
    :param force: force, defaults to None
    :type force: bool, optional
    """

    rollout_ids: List[str]
    force: Optional[bool] = Field(default=None)
