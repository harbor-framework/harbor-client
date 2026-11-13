from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel


class ModelIdentity(BaseModel):
    """ModelIdentity

    :param name: name
    :type name: str
    :param provider: provider
    :type provider: str
    :param reasoning_effort: reasoning_effort
    :type reasoning_effort: str
    """

    name: Optional[str]
    provider: Optional[str]
    reasoning_effort: Optional[str]
