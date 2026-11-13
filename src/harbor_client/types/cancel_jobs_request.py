from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class CancelJobsRequest(BaseModel):
    """CancelJobsRequest

    :param job_ids: job_ids
    :type job_ids: List[str]
    :param force: force, defaults to None
    :type force: bool, optional
    """

    job_ids: List[str]
    force: Optional[bool] = Field(default=None)
