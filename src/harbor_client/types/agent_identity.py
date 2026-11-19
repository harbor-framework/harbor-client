from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel


class AgentIdentity(BaseModel):
    """AgentIdentity

    :param name: name
    :type name: str
    :param version: version
    :type version: str
    """

    name: Optional[str]
    version: Optional[str]
