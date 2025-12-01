from pydantic import BaseModel, Field


class FrequencyEntry(BaseModel):
    """
    Reusable base entry for loss/claim/deduct frequency endpoints.
    """

    CustomerNum: str = Field(..., min_length=1)
    MthNum: int = Field(..., ge=1, le=12)
    Frequency: int | None = Field(None, ge=0)


class FrequencyPayload(BaseModel):
    items: list[FrequencyEntry]
