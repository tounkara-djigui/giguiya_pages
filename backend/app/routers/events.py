from fastapi import APIRouter, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from app.core.database import NO_ID, get_db
from app.core.utils import new_id, utcnow
from app.schemas.event import BookingCreatedOut, BookingIn, EventOut
from app.services import email_templates as tpl
from app.services.email_service import try_send_email
from app.services.event_service import booking_counts, event_out, events_out

router = APIRouter(prefix="/events", tags=["events"])
DUPLICATE_MSG = "Sei già iscritto a questo evento con questa email"


async def _published_event(slug: str) -> dict:
    event = await get_db().events.find_one({"$or": [{"slug": slug}, {"id": slug}], "is_published": True}, NO_ID)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato")
    return event


@router.get("", response_model=list[EventOut])
async def list_events(scope: str = Query("upcoming", pattern="^(upcoming|past|all)$"), category: str | None = None):
    query: dict = {"is_published": True}
    now = utcnow()
    sort = -1
    if scope == "upcoming":
        query["start_at"], sort = {"$gte": now}, 1
    elif scope == "past":
        query["start_at"] = {"$lt": now}
    if category:
        query["category"] = category
    events = await get_db().events.find(query, NO_ID).sort("start_at", sort).to_list(500)
    return await events_out(events)


@router.get("/{slug}", response_model=EventOut)
async def get_event(slug: str):
    event = await _published_event(slug)
    return event_out(event, (await booking_counts([event["id"]])).get(event["id"], 0))


@router.post("/{slug}/bookings", response_model=BookingCreatedOut, status_code=201)
async def book_event(slug: str, data: BookingIn):
    event = await _published_event(slug)
    if event["start_at"] < utcnow():
        raise HTTPException(status_code=400, detail="Le prenotazioni per questo evento sono chiuse")
    email = data.email.lower()
    if await get_db().bookings.find_one({"event_id": event["id"], "email": email}, {"_id": 1}):
        raise HTTPException(status_code=409, detail=DUPLICATE_MSG)
    if event.get("capacity"):
        if (await booking_counts([event["id"]])).get(event["id"], 0) >= event["capacity"]:
            raise HTTPException(status_code=400, detail="Evento al completo")
    booking = {"id": new_id(), "event_id": event["id"], "first_name": data.first_name.strip(),
               "last_name": data.last_name.strip(), "email": email, "phone": data.phone or None,
               "created_at": utcnow()}
    try:
        await get_db().bookings.insert_one(dict(booking))
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail=DUPLICATE_MSG)
    subject, html = tpl.booking_confirmation(booking["first_name"], event)
    sent = await try_send_email(to=booking["email"], subject=subject, html=html)
    return BookingCreatedOut(id=booking["id"], message="Prenotazione confermata!", email_sent=sent)
