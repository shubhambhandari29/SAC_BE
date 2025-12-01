from pydantic import BaseModel, EmailStr, Field


class LossRunDistributionEntry(BaseModel):
    """
    Represents a single loss run distribution recipient.
    Requires the composite key (CustomerNum + EMailAddress) but allows
    additional columns to pass through to the DB layer unchanged.
    """

    CustomerNum: str = Field(..., min_length=1)
    EMailAddress: EmailStr

    class Config:
        extra = "allow"
