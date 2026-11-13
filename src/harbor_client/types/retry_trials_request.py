from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class RetryTrialsRequest(BaseModel):
    """RetryTrialsRequest

    :param trial_ids: trial_ids
    :type trial_ids: List[str]
    """

    trial_ids: List[str]
