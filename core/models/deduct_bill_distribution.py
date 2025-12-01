from pydantic import BaseModel, EmailStr, Field


class DeductBillDistributionEntry(BaseModel):
    CustomerNum: str = Field(..., min_length=1)
    EMailAddress: EmailStr

    class Config:
        extra = "allow"
