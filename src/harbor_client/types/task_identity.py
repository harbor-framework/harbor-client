from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel


class TaskIdentity(BaseModel):
    """TaskIdentity

    :param name: name
    :type name: str
    :param digest: digest
    :type digest: str
    :param source: source
    :type source: str
    """

    name: str
    digest: str
    source: Optional[str]
