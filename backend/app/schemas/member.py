from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class MemberRegisterIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)
    birth_date: date | None = None
    birth_place: str | None = Field(default=None, max_length=120)
    fiscal_code: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=200)
    city: str | None = Field(default=None, max_length=100)
    privacy_accepted: bool

    @field_validator("privacy_accepted")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        if not v:
            raise ValueError("È necessario accettare l'informativa privacy e lo statuto")
        return v


class MemberUpdateIn(BaseModel):
    enrollment_paid: bool | None = None
    card_issued: bool | None = None
    notes: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None


class FeeToggleIn(BaseModel):
    paid: bool


class FeeOut(BaseModel):
    year: int
    amount: int
    paid_at: datetime


class MemberBookingOut(BaseModel):
    id: str
    event_title: str
    event_slug: str
    event_start: datetime
    created_at: datetime


class MemberOut(BaseModel):
    id: str
    user_id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None
    membership_number: str
    birth_date: date | None
    birth_place: str | None
    fiscal_code: str | None
    address: str | None
    city: str | None
    enrollment_paid: bool
    enrollment_paid_at: datetime | None
    card_issued: bool
    card_issued_at: datetime | None
    notes: str | None
    created_at: datetime
    account_active: bool
    fees: list[FeeOut]
    current_year: int
    current_year_paid: bool
    in_good_standing: bool
    enrollment_fee: str
    annual_fee: str


class MemberDashboardOut(BaseModel):
    member: MemberOut
    bookings: list[MemberBookingOut]
