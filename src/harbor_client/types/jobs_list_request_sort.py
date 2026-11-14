from __future__ import annotations
import typing
from typing import Any

JobsListRequestSort = typing.Union[
    typing.Literal[
        "id",
        "-id",
        "name",
        "-name",
        "state",
        "-state",
        "created_at",
        "-created_at",
        "started_at",
        "-started_at",
        "finished_at",
        "-finished_at",
    ],
    typing.Any,
]
