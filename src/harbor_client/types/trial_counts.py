from __future__ import annotations
from pydantic import Field
from typing import Optional
from typing import Any
from .utils.base_model import BaseModel


class TrialCounts(BaseModel):
    """TrialCounts

    :param n_total: n_total
    :type n_total: int
    :param n_queued: n_queued
    :type n_queued: int
    :param n_running: n_running
    :type n_running: int
    :param n_paused: n_paused
    :type n_paused: int
    :param n_cancelling: n_cancelling
    :type n_cancelling: int
    :param n_cancelled: n_cancelled
    :type n_cancelled: int
    :param n_finished: n_finished
    :type n_finished: int
    """

    n_total: int
    n_queued: int
    n_running: int
    n_paused: int
    n_cancelling: int
    n_cancelled: int
    n_finished: int
