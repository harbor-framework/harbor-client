from __future__ import annotations
from typing import Union
from typing import Any
from typing import Annotated
from pydantic import TypeAdapter
from .bad_request_encoded import BadRequestEncodedData
from .invalid_page_size_encoded import InvalidPageSizeEncoded
from .invalid_cursor_encoded import InvalidCursorEncoded


# fernMode variant type for a shared-component member of SecretsListBadRequestResponse
class SecretsListBadRequestResponse_BadRequest(BadRequestEncodedData):
    pass


# fernMode variant type for a shared-component member of SecretsListBadRequestResponse
class SecretsListBadRequestResponse_InvalidPageSize(InvalidPageSizeEncoded):
    pass


# fernMode variant type for a shared-component member of SecretsListBadRequestResponse
class SecretsListBadRequestResponse_InvalidCursor(InvalidCursorEncoded):
    pass


# Union type for SecretsListBadRequestResponse
# Pydantic will attempt to validate against each type in order
SecretsListBadRequestResponse = Union[
    BadRequestEncodedData, InvalidPageSizeEncoded, InvalidCursorEncoded
]
# TypeAdapter for runtime validation of SecretsListBadRequestResponse
# This allows validation of Union types which are not directly instantiable
from pydantic import TypeAdapter

SecretsListBadRequestResponse_adapter = TypeAdapter(SecretsListBadRequestResponse)
