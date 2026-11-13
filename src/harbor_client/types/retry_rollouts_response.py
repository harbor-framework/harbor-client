from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class RetryRolloutsResponse(BaseModel):
    """RetryRolloutsResponse

    :param rollout_ids: rollout_ids
    :type rollout_ids: List[str]
    """

    rollout_ids: List[str]
