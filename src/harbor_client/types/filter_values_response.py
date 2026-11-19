from __future__ import annotations
from enum import Enum
import typing
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel

FilterValuesResponseField = typing.Union[
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


class FilterValuesResponseValuesItem(BaseModel):
    """FilterValuesResponseValuesItem

    :param value: value
    :type value: str
    :param count: count
    :type count: int
    """

    value: str
    count: int


class FilterValuesResponseTruncated(Enum):
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
            map(lambda x: x.value, FilterValuesResponseTruncated._member_map_.values())
        )


class FilterValuesResponse(BaseModel):
    """FilterValuesResponse

    :param field: field
    :type field: FilterValuesResponseField
    :param values: values
    :type values: List[FilterValuesResponseValuesItem]
    :param truncated: truncated, defaults to None
    :type truncated: FilterValuesResponseTruncated, optional
    """

    field: FilterValuesResponseField
    values: List[FilterValuesResponseValuesItem]
    truncated: Optional[FilterValuesResponseTruncated] = Field(default=None)
