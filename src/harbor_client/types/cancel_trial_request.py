from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class CancelTrialRequest(BaseModel):
    """CancelTrialRequest

    :param force: force, defaults to None
    :type force: bool, optional
    """

    force: Optional[bool] = Field(default=None)
