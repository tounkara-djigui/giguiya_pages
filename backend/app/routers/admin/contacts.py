import re

from fastapi import APIRouter

from app.core.database import NO_ID, get_db
from app.schemas.admin import ContactOut
from app.services.event_service import event_titles

router = APIRouter(prefix="/contacts")


@router.get("", response_model=list[ContactOut])
async def list_contacts(q: str | None = None):
    query: dict = {}
    if q and q.strip():
        rx = {"$regex": re.escape(q.strip()), "$options": "i"}
        query["$or"] = [{"first_name": rx}, {"last_name": rx}, {"email": rx}]
    bookings = await get_db().bookings.find(query, NO_ID).sort("created_at", -1).to_list(10000)
    events = await event_titles([b["event_id"] for b in bookings])
    member_emails = set(await get_db().users.distinct("email", {"role": "member"}))
    contacts: dict[str, ContactOut] = {}
    for b in bookings:
        title = events.get(b["event_id"], {}).get("title", "Evento eliminato")
        c = contacts.get(b["email"])
        if not c:
            contacts[b["email"]] = ContactOut(
                email=b["email"], first_name=b["first_name"], last_name=b["last_name"], phone=b.get("phone"),
                bookings_count=1, last_booking_at=b["created_at"], events=[title], is_member=b["email"] in member_emails,
            )
        else:
            c.bookings_count += 1
            c.events.append(title)
            c.phone = c.phone or b.get("phone")
    return list(contacts.values())
