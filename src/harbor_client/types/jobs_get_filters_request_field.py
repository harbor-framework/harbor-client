from __future__ import annotations
import typing
from typing import Any

JobsGetFiltersRequestField = typing.Union[
    typing.Literal[
        "state",
        "task",
        "agent_name",
        "agent_version",
        "model_name",
        "model_provider",
        "reasoning_effort",
        "source",
    ],
    typing.Any,
]
