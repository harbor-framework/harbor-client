from __future__ import annotations
from typing import List
from pydantic import Field
from typing import Optional
from typing import Any
from typing import Union
from .utils.base_model import BaseModel
from .registry_credential_summary import RegistryCredentialSummary


class SecretsListRegistryCredentialsResponse(BaseModel):
    """SecretsListRegistryCredentialsResponse

    :param items: items
    :type items: List[RegistryCredentialSummary]
    :param next_cursor: Opaque cursor for the next page, or null on the last page. Pass it back unchanged as cursor; its contents and format may change without notice.
    :type next_cursor: str
    :param prev_cursor: Opaque cursor for the previous page, or null on the first page. Pass it back unchanged as cursor; its contents and format may change without notice.
    :type prev_cursor: str
    """

    items: List[RegistryCredentialSummary]
    next_cursor: Optional[str] = Field(
        description="Opaque cursor for the next page, or null on the last page. Pass it back unchanged as cursor; its contents and format may change without notice."
    )
    prev_cursor: Optional[str] = Field(
        description="Opaque cursor for the previous page, or null on the first page. Pass it back unchanged as cursor; its contents and format may change without notice."
    )
