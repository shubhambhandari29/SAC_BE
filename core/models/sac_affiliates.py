from pydantic import BaseModel, Field


class SacAffiliateUpsert(BaseModel):
    CustomerNum: str = Field(..., min_length=1)
    AffiliateName: str = Field(..., min_length=1)
