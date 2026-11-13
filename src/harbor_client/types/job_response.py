from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .job_detail import JobDetail


class JobResponse(BaseModel):
    """JobResponse

    :param job: job
    :type job: JobDetail
    """

    job: JobDetail
