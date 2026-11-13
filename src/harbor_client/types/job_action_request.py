from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class JobActionRequest(BaseModel):
    """JobActionRequest

    :param job_ids: One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order.
    :type job_ids: List[str]
    """

    job_ids: List[str] = Field(
        description="One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order."
    )
