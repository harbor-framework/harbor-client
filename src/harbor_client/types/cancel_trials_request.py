from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class CancelTrialsRequest(BaseModel):
    """CancelTrialsRequest

    :param trial_ids: One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order.
    :type trial_ids: List[str]
    :param force: force, defaults to None
    :type force: bool, optional
    """

    trial_ids: List[str] = Field(
        description="One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order."
    )
    force: Optional[bool] = Field(default=None)
