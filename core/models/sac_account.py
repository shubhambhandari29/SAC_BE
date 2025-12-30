
from pydantic import BaseModel, Field


class SacAccountUpsert(BaseModel):
    """
    Payload for creating or updating an SAC account row.
    Fields are optional so that business-rule validations handle errors uniformly.
    """

    CustomerNum: str | None = Field(None, min_length=1)
    CustomerName: str | None = None
    OnBoardDate: str | None = None
    ServLevel: str | None = None
    Stage: str | None = None
    IsSubmitted: int | None = None
    AcctOwner: str | None = None
    BusinessType: str | None = None
    BranchName: str | None = None

    class Config:
        extra = "allow"
