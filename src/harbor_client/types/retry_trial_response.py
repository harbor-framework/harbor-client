from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class RetryTrialResponse(BaseModel):
    """RetryTrialResponse

    :param trial_id: trial_id
    :type trial_id: str
    """

    trial_id: str
