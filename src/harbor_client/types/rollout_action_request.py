from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class RolloutActionRequest(BaseModel):
    """RolloutActionRequest

    :param rollout_ids: One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order.
    :type rollout_ids: List[str]
    """

    rollout_ids: List[str] = Field(
        description="One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order."
    )
