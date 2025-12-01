from datetime import date

from pydantic import BaseModel, Field


class SacAccountUpsert(BaseModel):
    """
    Payload for creating or updating an SAC account row.
    Only CustomerNum is mandatory; other fields are optional updates.
    """

    CustomerNum: str = Field(..., min_length=1)
    CustomerName: str | None = None
    OnBoardDate: date | None = None
    ServLevel: str | None = None
    Stage: str | None = None
    isSubmitted: bool | None = None
    AcctOwner: str | None = None
