from __future__ import annotations
from typing import Union
from typing import Any
from typing import Annotated
from pydantic import TypeAdapter
from .submit_job_response import SubmitJobResponse
from .dry_run_response import DryRunResponse

# Union type for JobsSubmitResponse
# Pydantic will attempt to validate against each type in order
JobsSubmitResponse = Union[SubmitJobResponse, DryRunResponse]
# TypeAdapter for runtime validation of JobsSubmitResponse
# This allows validation of Union types which are not directly instantiable

JobsSubmitResponse_adapter = TypeAdapter(JobsSubmitResponse)
