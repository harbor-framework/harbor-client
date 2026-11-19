from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .package_tag import PackageTag


class PackagesListTagsResponse(BaseModel):
    """PackagesListTagsResponse

    :param items: items
    :type items: List[PackageTag]
    :param next_cursor: Opaque cursor for the next page, or null on the last page. Pass it back unchanged as cursor; its contents and format may change without notice.
    :type next_cursor: str
    :param prev_cursor: Opaque cursor for the previous page, or null on the first page. Pass it back unchanged as cursor; its contents and format may change without notice.
    :type prev_cursor: str
    """

    items: List[PackageTag]
    next_cursor: Optional[str] = Field(
        description="Opaque cursor for the next page, or null on the last page. Pass it back unchanged as cursor; its contents and format may change without notice."
    )
    prev_cursor: Optional[str] = Field(
        description="Opaque cursor for the previous page, or null on the first page. Pass it back unchanged as cursor; its contents and format may change without notice."
    )
