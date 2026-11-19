from __future__ import annotations
from typing import Union
from typing import Any
from typing import Annotated
from pydantic import TypeAdapter
from .bad_request_encoded import BadRequestEncodedData
from .invalid_page_size_encoded import InvalidPageSizeEncoded
from .invalid_cursor_encoded import InvalidCursorEncoded


# fernMode variant type for a shared-component member of RolloutsListBadRequestResponse
class RolloutsListBadRequestResponse_BadRequest(BadRequestEncodedData):
    pass


# fernMode variant type for a shared-component member of RolloutsListBadRequestResponse
class RolloutsListBadRequestResponse_InvalidPageSize(InvalidPageSizeEncoded):
    pass


# fernMode variant type for a shared-component member of RolloutsListBadRequestResponse
class RolloutsListBadRequestResponse_InvalidCursor(InvalidCursorEncoded):
    pass


# Union type for RolloutsListBadRequestResponse
# Pydantic will attempt to validate against each type in order
RolloutsListBadRequestResponse = Union[
    BadRequestEncodedData, InvalidPageSizeEncoded, InvalidCursorEncoded
]
# TypeAdapter for runtime validation of RolloutsListBadRequestResponse
# This allows validation of Union types which are not directly instantiable
from pydantic import TypeAdapter

RolloutsListBadRequestResponse_adapter = TypeAdapter(RolloutsListBadRequestResponse)
