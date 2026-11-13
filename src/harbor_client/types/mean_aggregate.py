from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel


class MeanAggregate(BaseModel):
    """MeanAggregate

    :param mean: mean
    :type mean: float
    :param count: count
    :type count: int
    """

    mean: Optional[float]
    count: int
