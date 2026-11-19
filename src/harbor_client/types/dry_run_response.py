from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class DryRunResponse(BaseModel):
    """DryRunResponse

    :param n_trials: n_trials
    :type n_trials: int
    """

    n_trials: int
