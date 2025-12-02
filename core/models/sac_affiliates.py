from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SacAffiliateUpsert(BaseModel):
    CustomerNum: str = Field(..., min_length=1)
    AffiliateName: str = Field(..., min_length=1)
    Email: Optional[EmailStr] = None

    class Config:
        extra = "allow"
