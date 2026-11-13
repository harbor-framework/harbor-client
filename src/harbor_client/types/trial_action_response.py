from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .trial_detail import TrialDetail


class TrialActionResponse(BaseModel):
    """TrialActionResponse

    :param items: items
    :type items: List[TrialDetail]
    """

    items: List[TrialDetail]
