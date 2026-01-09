from pydantic import BaseModel, EmailStr, Field


class HCMUserUpsert(BaseModel):
    PK_Number: int | None = None
    UserTitle: str | None = None
    UserID: str | None = None
    UserName: str | None = None
    UserEmail: EmailStr | None = None
    TelNum: str | None = None
    TelExt: int | None = None
    UserAction: str | None = None
    CustomerNum: str | None = None
    LanID: str | None = None
    PROD_Password: str | None = None
    UAT_Password: str | None = None
