from __future__ import annotations
from typing import Union
from typing import Any
from typing import Annotated
from pydantic import TypeAdapter
from .cancel_trials_by_id_request import CancelTrialsByIdRequest
from .cancel_trials_by_filter_request import CancelTrialsByFilterRequest
from .cancel_all_job_trials_request import CancelAllJobTrialsRequest

# Union type for CancelTrialsRequest
# Pydantic will attempt to validate against each type in order
CancelTrialsRequest = Union[
    CancelTrialsByIdRequest, CancelTrialsByFilterRequest, CancelAllJobTrialsRequest
]
# TypeAdapter for runtime validation of CancelTrialsRequest
# This allows validation of Union types which are not directly instantiable
from pydantic import TypeAdapter

CancelTrialsRequest_adapter = TypeAdapter(CancelTrialsRequest)

    :param trial_ids: One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order.
    :type trial_ids: List[str]
    :param force: force, defaults to None
    :type force: bool, optional
    """

    trial_ids: List[str] = Field(
        description="One to 100 IDs per request. Repeated IDs count toward the limit; results contain each ID once in first-occurrence order."
    )
    force: Optional[bool] = Field(default=None)
