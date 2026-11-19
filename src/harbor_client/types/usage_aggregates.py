from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .sum_aggregate import SumAggregate


class UsageAggregates(BaseModel):
    """UsageAggregates

    :param n_input_tokens: n_input_tokens
    :type n_input_tokens: SumAggregate
    :param n_cached_input_tokens: n_cached_input_tokens
    :type n_cached_input_tokens: SumAggregate
    :param n_output_tokens: n_output_tokens
    :type n_output_tokens: SumAggregate
    :param cost_usd: cost_usd
    :type cost_usd: SumAggregate
    """

    n_input_tokens: SumAggregate
    n_cached_input_tokens: SumAggregate
    n_output_tokens: SumAggregate
    cost_usd: SumAggregate
