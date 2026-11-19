from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel


class SumAggregate(BaseModel):
    """SumAggregate

    :param sum: sum
    :type sum: float
    :param count: count
    :type count: int
    """

    sum: Optional[float]
    count: int
