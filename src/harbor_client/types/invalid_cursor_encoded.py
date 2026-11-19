from __future__ import annotations
from enum import Enum
import typing
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel

InvalidCursorEncodedTag = typing.Union[typing.Literal["InvalidCursor"], typing.Any]

InvalidCursorEncodedType = typing.Union[
    typing.Literal["https://api.harborframework.com/problems/invalid-cursor"],
    typing.Any,
]

InvalidCursorEncodedTitle = typing.Union[typing.Literal["Invalid cursor"], typing.Any]


class InvalidCursorEncodedStatus(float, Enum):
    """An enumeration representing different categories.

    :cvar _400: 400
    :vartype _400: float
    """

    _400 = 400

    @staticmethod
    def list():
        """Lists all enum values.

        :return: A list of all enum values.
        :rtype: list
        """
        return list(
            map(lambda x: x.value, InvalidCursorEncodedStatus._member_map_.values())
        )


InvalidCursorEncodedDetail = typing.Union[
    typing.Literal[
        "cursor is invalid, expired, or was issued for a different request. Request the list again without cursor to start from the first page."
    ],
    typing.Any,
]


class InvalidCursorEncoded(BaseModel):
    """InvalidCursorEncoded

    :param tag: tag
    :type tag: InvalidCursorEncodedTag
    :param type: The cursor can't be used: it is malformed, from an older cursor format, or was issued for a request with different parameters, such as other filters or sort. Cursors are opaque and may stop working when their format changes. Request the list again without cursor to start from the first page.
    :type type: InvalidCursorEncodedType
    :param title: title
    :type title: InvalidCursorEncodedTitle
    :param status: status
    :type status: InvalidCursorEncodedStatus
    :param detail: detail
    :type detail: InvalidCursorEncodedDetail
    """

    tag: InvalidCursorEncodedTag = Field(
        alias="_tag", serialization_alias="_tag", default="InvalidCursor"
    )
    type: InvalidCursorEncodedType = Field(
        default="https://api.harborframework.com/problems/invalid-cursor",
        description="The cursor can't be used: it is malformed, from an older cursor format, or was issued for a request with different parameters, such as other filters or sort. Cursors are opaque and may stop working when their format changes. Request the list again without cursor to start from the first page.",
    )
    title: InvalidCursorEncodedTitle = Field(default="Invalid cursor")
    status: InvalidCursorEncodedStatus = Field(default=400)
    detail: InvalidCursorEncodedDetail = Field(
        default="cursor is invalid, expired, or was issued for a different request. Request the list again without cursor to start from the first page."
    )
