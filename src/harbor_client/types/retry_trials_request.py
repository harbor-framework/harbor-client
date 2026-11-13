from __future__ import annotations
from typing import Union
from typing import Any
from typing import Annotated
from pydantic import TypeAdapter
from .retry_trials_by_id_request import RetryTrialsByIdRequest
from .retry_trials_by_filter_request import RetryTrialsByFilterRequest
from .retry_all_job_trials_request import RetryAllJobTrialsRequest

# Union type for RetryTrialsRequest
# Pydantic will attempt to validate against each type in order
RetryTrialsRequest = Union[
    RetryTrialsByIdRequest, RetryTrialsByFilterRequest, RetryAllJobTrialsRequest
]
# TypeAdapter for runtime validation of RetryTrialsRequest
# This allows validation of Union types which are not directly instantiable
from pydantic import TypeAdapter

RetryTrialsRequest_adapter = TypeAdapter(RetryTrialsRequest)

    :param trial_ids: One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order.
    :type trial_ids: List[str]
    """

    trial_ids: List[str] = Field(
        description="One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order."
    )
