from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import utcnow
from app.models import Booking, Event
from app.schemas.event import BookingCreatedOut, BookingIn, EventOut
from app.services import email_templates as tpl
from app.services.email_service import try_send_email
from app.services.event_service import booking_counts, event_out, events_out

router = APIRouter(prefix="/events", tags=["events"])


async def _published_event(db: AsyncSession, slug: str) -> Event:
    event = (await db.execute(
        select(Event).where(or_(Event.slug == slug, Event.id == slug), Event.is_published.is_(True))
    )).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


@router.get("", response_model=list[EventOut])
async def list_events(scope: str = Query("upcoming", pattern="^(upcoming|past|all)$"),
                      category: str | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Event).where(Event.is_published.is_(True))
    now = utcnow()
    if scope == "upcoming":
        q = q.where(Event.start_at >= now).order_by(Event.start_at.asc())
    elif scope == "past":
        q = q.where(Event.start_at < now).order_by(Event.start_at.desc())
    else:
        q = q.order_by(Event.start_at.desc())
    if category:
        q = q.where(Event.category == category)
    return await events_out(db, list((await db.execute(q)).scalars().all()))


@router.get("/{slug}", response_model=EventOut)
async def get_event(slug: str, db: AsyncSession = Depends(get_db)):
    event = await _published_event(db, slug)
    counts = await booking_counts(db, [event.id])
    return event_out(event, counts.get(event.id, 0))


@router.post("/{slug}/bookings", response_model=BookingCreatedOut, status_code=201)
async def book_event(slug: str, data: BookingIn, db: AsyncSession = Depends(get_db)):
    event = await _published_event(db, slug)
    if event.start_at < utcnow():
        raise HTTPException(status_code=400, detail="Le prenotazioni per questo evento sono chiuse")
    if event.capacity:
        count = (await booking_counts(db, [event.id])).get(event.id, 0)
        if count >= event.capacity:
            raise HTTPException(status_code=400, detail="Evento al completo")
    booking = Booking(event_id=event.id, first_name=data.first_name.strip(), last_name=data.last_name.strip(),
                      email=data.email.lower(), phone=data.phone or None)
    db.add(booking)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Sei già iscritto a questo evento con questa email")
    subject, html = tpl.booking_confirmation(booking.first_name, event)
    sent = await try_send_email(to=booking.email, subject=subject, html=html)
    return BookingCreatedOut(id=booking.id, message="Prenotazione confermata!", email_sent=sent)
