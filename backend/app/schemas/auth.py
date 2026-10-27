from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class AdminRegisterIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenIn(BaseModel):
    token: str = Field(min_length=10)


class SetPasswordIn(TokenIn):
    password: str = Field(min_length=8, max_length=128)


class EmailIn(BaseModel):
    email: EmailStr


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    role: str
    is_super_admin: bool = False


class StaffOut(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    email_verified: bool = False
    admin_status: str = "pending"
    created_at: datetime


class MessageOut(BaseModel):
    message: str
    email_sent: bool | None = None
