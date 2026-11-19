from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class AgentsResponse(BaseModel):
    """AgentsResponse

    :param agents: agents
    :type agents: List[str]
    """

    agents: List[str]
