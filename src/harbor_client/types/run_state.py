from __future__ import annotations
import typing
from typing import Any

RunState = typing.Union[
    typing.Literal[
        "queued", "running", "paused", "cancelling", "finished", "cancelled"
    ],
    typing.Any,
]
