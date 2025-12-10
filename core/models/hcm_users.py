from pydantic import BaseModel, EmailStr, Field


class HCMUserUpsert(BaseModel):
    UserTitle: str | None = None
    UserID: str = Field(..., min_length=1)
    UserName: str | None = None
    UserEmail: EmailStr | None = None
    TelNum: int | None = None
    TelExt: int | None = None
    UserAction: str | None = None
    CustomerNum: str = Field(..., min_length=1)
    LanID: str | None = None
    PROD_Password: str | None = None
    UAT_Password: str | None = None
