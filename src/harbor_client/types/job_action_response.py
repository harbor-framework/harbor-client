from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .job_detail import JobDetail


class JobActionResponse(BaseModel):
    """JobActionResponse

    :param items: items
    :type items: List[JobDetail]
    """

    items: List[JobDetail]
