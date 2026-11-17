from typing import TYPE_CHECKING

from .client import HarborAPIClient, AsyncHarborAPIClient
from .net.environment import HarborApiClientEnvironment
from .version import __version__
from .errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnauthorizedError,
)

if TYPE_CHECKING:
    from .validation import ContractError
    from .transfers import StorageTransferError, UploadFile

from . import types as _models

import importlib

_LAZY_EXPORTS = {
    "ContractError": ".validation",
    "StorageTransferError": ".transfers",
    "UploadFile": ".transfers",
}


def __getattr__(name):
    """Falls back to the lazy ``.types`` registry for any name not re-exported above."""
    module = _LAZY_EXPORTS.get(name)
    if module is not None:
        value = getattr(importlib.import_module(module, __name__), name)
        globals()[name] = value
        return value
    try:
        return getattr(_models, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None


def __dir__():
    return sorted(set(globals()) | set(dir(_models)) | set(_LAZY_EXPORTS))

# Preserve the established environment import across generator naming changes.
from .net.environment import HarborAPIClientEnvironment
