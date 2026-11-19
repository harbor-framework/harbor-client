from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .trial_detail import TrialDetail


class TrialResponse(BaseModel):
    """TrialResponse

    :param trial: trial
    :type trial: TrialDetail
    """

    trial: TrialDetail
