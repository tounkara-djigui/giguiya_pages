from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Booking, User
from app.schemas.admin import ContactOut

router = APIRouter(prefix="/contacts")


@router.get("", response_model=list[ContactOut])
async def list_contacts(q: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Booking).order_by(Booking.created_at.desc())
    if q:
        like = f"%{q.strip()}%"
        query = query.where(or_(Booking.first_name.ilike(like), Booking.last_name.ilike(like), Booking.email.ilike(like)))
    bookings = (await db.execute(query)).scalars().all()
    member_emails = set((await db.execute(select(User.email).where(User.role == "member"))).scalars().all())
    contacts: dict[str, ContactOut] = {}
    for b in bookings:
        c = contacts.get(b.email)
        if not c:
            contacts[b.email] = ContactOut(
                email=b.email, first_name=b.first_name, last_name=b.last_name, phone=b.phone,
                bookings_count=1, last_booking_at=b.created_at, events=[b.event.title],
                is_member=b.email in member_emails,
            )
        else:
            c.bookings_count += 1
            c.events.append(b.event.title)
            c.phone = c.phone or b.phone
    return list(contacts.values())
