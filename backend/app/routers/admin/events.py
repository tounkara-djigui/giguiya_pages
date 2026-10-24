from fastapi import APIRouter, HTTPException

from app.core.database import NO_ID, get_db
from app.core.utils import localize, new_id, utcnow
from app.schemas.auth import MessageOut
from app.schemas.event import BookingOut, EventIn, EventOut
from app.services.event_service import event_out, events_out, unique_slug

router = APIRouter()


async def _get_event(event_id: str) -> dict:
    event = await get_db().events.find_one({"id": event_id}, NO_ID)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


def _values(data: EventIn) -> dict:
    values = data.model_dump()
    values["start_at"], values["end_at"] = localize(data.start_at), localize(data.end_at)
    if values["end_at"] and values["end_at"] < values["start_at"]:
        raise HTTPException(status_code=400, detail="La data di fine deve essere successiva all'inizio")
    return values


@router.get("/events", response_model=list[EventOut])
async def list_events():
    return await events_out(await get_db().events.find({}, NO_ID).sort("start_at", -1).to_list(2000))


@router.post("/events", response_model=EventOut, status_code=201)
async def create_event(data: EventIn):
    event = {**_values(data), "id": new_id(), "slug": await unique_slug(get_db().events, data.title), "created_at": utcnow()}
    await get_db().events.insert_one(dict(event))
    return event_out(event)


@router.put("/events/{event_id}", response_model=EventOut)
async def update_event(event_id: str, data: EventIn):
    event = await _get_event(event_id)
    values = _values(data)
    if data.title != event["title"]:
        values["slug"] = await unique_slug(get_db().events, data.title, exclude_id=event_id)
    await get_db().events.update_one({"id": event_id}, {"$set": values})
    return (await events_out([await _get_event(event_id)]))[0]


@router.delete("/events/{event_id}", response_model=MessageOut)
async def delete_event(event_id: str):
    await _get_event(event_id)
    await get_db().events.delete_one({"id": event_id})
    await get_db().bookings.delete_many({"event_id": event_id})
    return MessageOut(message="Evento eliminato")


@router.get("/events/{event_id}/bookings", response_model=list[BookingOut])
async def event_bookings(event_id: str):
    event = await _get_event(event_id)
    rows = await get_db().bookings.find({"event_id": event_id}, NO_ID).sort("created_at", -1).to_list(5000)
    return [BookingOut(**b, event_title=event["title"]) for b in rows]


@router.delete("/bookings/{booking_id}", response_model=MessageOut)
async def delete_booking(booking_id: str):
    result = await get_db().bookings.delete_one({"id": booking_id})
    if not result.deleted_count:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    return MessageOut(message="Prenotazione eliminata")
