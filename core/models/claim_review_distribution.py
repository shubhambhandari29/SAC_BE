from pydantic import BaseModel, EmailStr, Field


class ClaimReviewDistributionEntry(BaseModel):
    """
    Keyed by CustomerNum + EMailAddress; allows additional columns to pass through.
    """

    CustomerNum: str = Field(..., min_length=1)
    EMailAddress: EmailStr

    class Config:
        extra = "allow"
