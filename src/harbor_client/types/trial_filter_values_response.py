from __future__ import annotations
from enum import Enum
import typing
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel

TrialFilterValuesResponseField = typing.Union[
    typing.Literal[
        "state",
        "error_type",
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


class TrialFilterValuesResponseValuesItem(BaseModel):
    """TrialFilterValuesResponseValuesItem

    :param value: value
    :type value: str
    :param count: count
    :type count: int
    """

    value: str
    count: int


class TrialFilterValuesResponseTruncated(Enum):
    """An enumeration representing different categories.

    :cvar TRUE: True
    :vartype TRUE: str
    """

    TRUE = True

    @staticmethod
    def list():
        """Lists all enum values.

        :return: A list of all enum values.
        :rtype: list
        """
        return list(
            map(
                lambda x: x.value,
                TrialFilterValuesResponseTruncated._member_map_.values(),
            )
        )


class TrialFilterValuesResponse(BaseModel):
    """TrialFilterValuesResponse

    :param field: field
    :type field: TrialFilterValuesResponseField
    :param values: values
    :type values: List[TrialFilterValuesResponseValuesItem]
    :param truncated: truncated, defaults to None
    :type truncated: TrialFilterValuesResponseTruncated, optional
    """

    field: TrialFilterValuesResponseField
    values: List[TrialFilterValuesResponseValuesItem]
    truncated: Optional[TrialFilterValuesResponseTruncated] = Field(default=None)
