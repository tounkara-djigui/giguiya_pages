import re

from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError

from app.core.database import NO_ID, get_db
from app.core.security import require_member
from app.core.utils import current_year, new_id, utcnow
from app.schemas.auth import MessageOut
from app.schemas.member import MemberBookingOut, MemberDashboardOut, MemberRegisterIn
from app.services import email_templates as tpl
from app.services.email_service import try_send_email
from app.services.event_service import event_titles
from app.services.member_service import member_out
from app.services.token_service import issue_token

router = APIRouter(prefix="/members", tags=["members"])


async def next_membership_number() -> str:
    prefix = f"GIG-{current_year()}-"
    last = await get_db().users.find_one(
        {"member.membership_number": {"$regex": f"^{re.escape(prefix)}"}},
        {"member.membership_number": 1}, sort=[("member.membership_number", -1)],
    )
    seq = int(last["member"]["membership_number"].rsplit("-", 1)[1]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


async def send_member_invite(user: dict) -> bool:
    raw = await issue_token(user["id"], "set_password", hours=24 * 7)
    subject, html = tpl.member_welcome(user["first_name"], user["member"]["membership_number"], raw)
    return await try_send_email(to=user["email"], subject=subject, html=html)


async def _email_taken(email: str) -> bool:
    return bool(await get_db().users.find_one({"email": email}, {"_id": 1}))


@router.post("/register", response_model=MessageOut, status_code=201)
async def register_member(data: MemberRegisterIn):
    email = data.email.lower()
    if await _email_taken(email):
        raise HTTPException(status_code=409, detail="Esiste già un account con questa email")
    now = utcnow()
    user = {
        "id": new_id(), "email": email, "role": "member", "email_verified": False, "password_hash": None,
        "first_name": data.first_name.strip(), "last_name": data.last_name.strip(), "phone": data.phone or None,
        "created_at": now,
        "member": {
            "birth_date": data.birth_date.isoformat() if data.birth_date else None, "birth_place": data.birth_place,
            "fiscal_code": (data.fiscal_code or "").upper() or None, "address": data.address, "city": data.city,
            "enrollment_paid": False, "enrollment_paid_at": None, "card_issued": False, "card_issued_at": None,
            "notes": None, "fees": [], "created_at": now,
        },
    }
    for _ in range(5):
        user["member"]["membership_number"] = await next_membership_number()
        try:
            await get_db().users.insert_one(dict(user))
            break
        except DuplicateKeyError:
            if await _email_taken(email):
                raise HTTPException(status_code=409, detail="Esiste già un account con questa email")
    else:
        raise HTTPException(status_code=503, detail="Riprova tra qualche istante")
    sent = await send_member_invite(user)
    return MessageOut(message="Domanda di iscrizione ricevuta! Controlla la tua email.", email_sent=sent)


@router.get("/me", response_model=MemberDashboardOut)
async def my_membership(user: dict = Depends(require_member)):
    bookings = await get_db().bookings.find({"email": user["email"]}, NO_ID).sort("created_at", -1).to_list(500)
    events = await event_titles([b["event_id"] for b in bookings])
    return MemberDashboardOut(
        member=member_out(user),
        bookings=[MemberBookingOut(id=b["id"], event_title=events[b["event_id"]]["title"],
                                   event_slug=events[b["event_id"]]["slug"],
                                   event_start=events[b["event_id"]]["start_at"], created_at=b["created_at"])
                  for b in bookings if b["event_id"] in events],
    )
