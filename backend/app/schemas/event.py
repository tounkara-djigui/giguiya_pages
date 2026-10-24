from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class EventIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    summary: str = Field(default="", max_length=400)
    description: str = ""
    category: str = Field(default="Cultura", max_length=60)
    location: str = Field(default="", max_length=200)
    start_at: datetime
    end_at: datetime | None = None
    image_url: str | None = Field(default=None, max_length=500)
    capacity: int | None = Field(default=None, ge=1)
    price_label: str | None = Field(default=None, max_length=60)
    is_published: bool = True


class EventOut(EventIn):
    id: str
    slug: str
    bookings_count: int = 0
    spots_left: int | None = None
    start_local: str | None = None
    end_local: str | None = None
    is_past: bool = False


class BookingIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=40)


class BookingOut(BaseModel):
    id: str
    event_id: str
    event_title: str
    first_name: str
    last_name: str
    email: str
    phone: str | None
    created_at: datetime


class BookingCreatedOut(BaseModel):
    id: str
    message: str
    email_sent: bool
