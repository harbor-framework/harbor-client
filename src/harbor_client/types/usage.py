from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel


class Usage(BaseModel):
    """Usage

    :param n_input_tokens: n_input_tokens
    :type n_input_tokens: float
    :param n_cached_input_tokens: n_cached_input_tokens
    :type n_cached_input_tokens: float
    :param n_output_tokens: n_output_tokens
    :type n_output_tokens: float
    :param cost_usd: cost_usd
    :type cost_usd: float
    """

    n_input_tokens: Optional[float]
    n_cached_input_tokens: Optional[float]
    n_output_tokens: Optional[float]
    cost_usd: Optional[float]
