from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .trial_detail1 import TrialDetail1


class RolloutResponse(BaseModel):
    """RolloutResponse

    :param rollout: rollout
    :type rollout: TrialDetail1
    """

    rollout: TrialDetail1
