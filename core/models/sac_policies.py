from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class SacPolicyUpsert(BaseModel):
    """
    Payload for inserting or updating a SAC policy record.
    PK_Number (identity column) is preferred when updating an existing row.
    """

    PK_Number: int | None = None
    CustomerNum: str = Field(..., min_length=1)
    PolicyNum: str = Field(..., min_length=1)
    PolMod: str = Field(..., min_length=1)
    AccountActiveYN: str | None = None
    AccountName: str | None = None
    AcctOnPolicyName: str | None = None
    PremiumAmt: str | None = None
    PolicyType: str | None = None
    AgentCode: str | None = None
    AgentName: str | None = None
    InceptDate: str | None = None


class SacPolicyBulkFieldUpdate(BaseModel):
    """
    Request body for /sac_policies/update_field_for_all_policies.
    """

    fieldName: Literal["AccountName", "AcctOnPolicyName", "AcctOwner", "AccountActiveYN"]
    fieldValue: str | bool
    updateVia: Literal["CustomerNum", "PolicyNum", "PolMod"]
    updateViaValue: str = Field(..., min_length=1)
