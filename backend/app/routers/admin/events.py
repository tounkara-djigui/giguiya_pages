from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import localize
from app.models import Booking, Event
from app.schemas.auth import MessageOut
from app.schemas.event import BookingOut, EventIn, EventOut
from app.services.event_service import event_out, events_out, unique_slug

router = APIRouter()


async def _get_event(db: AsyncSession, event_id: str) -> Event:
    event = await db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


def _apply(event: Event, data: EventIn) -> None:
    values = data.model_dump()
    values["start_at"], values["end_at"] = localize(data.start_at), localize(data.end_at)
    if values["end_at"] and values["end_at"] < values["start_at"]:
        raise HTTPException(status_code=400, detail="La data di fine deve essere successiva all'inizio")
    for k, v in values.items():
        setattr(event, k, v)


@router.get("/events", response_model=list[EventOut])
async def list_events(db: AsyncSession = Depends(get_db)):
    events = (await db.execute(select(Event).order_by(Event.start_at.desc()))).scalars().all()
    return await events_out(db, list(events))


@router.post("/events", response_model=EventOut, status_code=201)
async def create_event(data: EventIn, db: AsyncSession = Depends(get_db)):
    event = Event(slug=await unique_slug(db, Event, data.title))
    _apply(event, data)
    db.add(event)
    await db.commit()
    return event_out(event)


@router.put("/events/{event_id}", response_model=EventOut)
async def update_event(event_id: str, data: EventIn, db: AsyncSession = Depends(get_db)):
    event = await _get_event(db, event_id)
    if data.title != event.title:
        event.slug = await unique_slug(db, Event, data.title, exclude_id=event.id)
    _apply(event, data)
    await db.commit()
    return (await events_out(db, [event]))[0]


@router.delete("/events/{event_id}", response_model=MessageOut)
async def delete_event(event_id: str, db: AsyncSession = Depends(get_db)):
    await db.delete(await _get_event(db, event_id))
    await db.commit()
    return MessageOut(message="Evento eliminato")


@router.get("/events/{event_id}/bookings", response_model=list[BookingOut])
async def event_bookings(event_id: str, db: AsyncSession = Depends(get_db)):
    event = await _get_event(db, event_id)
    rows = (await db.execute(
        select(Booking).where(Booking.event_id == event.id).order_by(Booking.created_at.desc())
    )).scalars().all()
    return [BookingOut(id=b.id, event_id=b.event_id, event_title=event.title, first_name=b.first_name,
                       last_name=b.last_name, email=b.email, phone=b.phone, created_at=b.created_at) for b in rows]


@router.delete("/bookings/{booking_id}", response_model=MessageOut)
async def delete_booking(booking_id: str, db: AsyncSession = Depends(get_db)):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    await db.delete(booking)
    await db.commit()
    return MessageOut(message="Prenotazione eliminata")
