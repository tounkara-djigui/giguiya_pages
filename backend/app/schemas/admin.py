from datetime import datetime

from pydantic import BaseModel


class ContactOut(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone: str | None
    bookings_count: int
    last_booking_at: datetime
    events: list[str]
    is_member: bool


class StatsOut(BaseModel):
    members_total: int
    members_in_good_standing: int
    members_pending_card: int
    members_pending_enrollment: int
    bookings_total: int
    contacts_total: int
    upcoming_events: int
    projects_total: int
    current_year: int
