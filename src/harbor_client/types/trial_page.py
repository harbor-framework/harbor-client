from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .trial_summary import TrialSummary


class TrialPage(BaseModel):
    """TrialPage

    :param items: items
    :type items: List[TrialSummary]
    :param total: total
    :type total: int
    :param next_page_token: next_page_token
    :type next_page_token: str
    """

    items: List[TrialSummary]
    total: int
    next_page_token: str
