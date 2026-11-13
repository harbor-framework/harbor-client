from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class RetryRolloutResponse(BaseModel):
    """RetryRolloutResponse

    :param rollout_id: rollout_id
    :type rollout_id: str
    """

    rollout_id: str
