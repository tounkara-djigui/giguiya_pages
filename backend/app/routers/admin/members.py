import re

from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.core.database import NO_ID, get_db
from app.core.utils import utcnow
from app.routers.members import send_member_invite
from app.schemas.auth import MessageOut
from app.schemas.member import FeeToggleIn, MemberOut, MemberUpdateIn
from app.services.member_service import member_out

router = APIRouter(prefix="/members")

STATUS_FILTERS = {
    "in_regola": lambda m: m.in_good_standing,
    "non_in_regola": lambda m: not m.in_good_standing,
    "tessera_da_rilasciare": lambda m: not m.card_issued,
}


async def _get_member(member_id: str) -> dict:
    user = await get_db().users.find_one({"id": member_id, "role": "member"}, NO_ID)
    if not user:
        raise HTTPException(status_code=404, detail="Socio non trovato")
    return user


@router.get("", response_model=list[MemberOut])
async def list_members(q: str | None = None, status: str = Query("all")):
    query: dict = {"role": "member"}
    if q and q.strip():
        rx = {"$regex": re.escape(q.strip()), "$options": "i"}
        query["$or"] = [{"first_name": rx}, {"last_name": rx}, {"email": rx}, {"member.membership_number": rx}]
    users = await get_db().users.find(query, NO_ID).sort([("last_name", 1), ("first_name", 1)]).to_list(5000)
    members = [member_out(u) for u in users]
    if status in STATUS_FILTERS:
        members = [m for m in members if STATUS_FILTERS[status](m)]
    return members


@router.get("/{member_id}", response_model=MemberOut)
async def get_member(member_id: str):
    return member_out(await _get_member(member_id))


@router.patch("/{member_id}", response_model=MemberOut)
async def update_member(member_id: str, data: MemberUpdateIn):
    await _get_member(member_id)
    changes = data.model_dump(exclude_unset=True)
    update: dict = {}
    for flag, stamp in (("enrollment_paid", "enrollment_paid_at"), ("card_issued", "card_issued_at")):
        if flag in changes:
            update[f"member.{flag}"] = bool(changes[flag])
            update[f"member.{stamp}"] = utcnow() if changes[flag] else None
    for field in ("notes", "address", "city"):
        if field in changes:
            update[f"member.{field}"] = changes[field]
    if "phone" in changes:
        update["phone"] = changes["phone"]
    if update:
        await get_db().users.update_one({"id": member_id}, {"$set": update})
    return member_out(await _get_member(member_id))


@router.put("/{member_id}/fees/{year}", response_model=MemberOut)
async def toggle_fee(member_id: str, year: int, data: FeeToggleIn):
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Anno non valido")
    user = await _get_member(member_id)
    paid = any(f["year"] == year for f in user["member"].get("fees", []))
    if data.paid and not paid:
        fee = {"year": year, "amount": settings.ANNUAL_FEE, "paid_at": utcnow()}
        await get_db().users.update_one({"id": member_id}, {"$push": {"member.fees": fee}})
    elif not data.paid and paid:
        await get_db().users.update_one({"id": member_id}, {"$pull": {"member.fees": {"year": year}}})
    return member_out(await _get_member(member_id))


@router.post("/{member_id}/resend-invite", response_model=MessageOut)
async def resend_invite(member_id: str):
    sent = await send_member_invite(await _get_member(member_id))
    return MessageOut(message="Email di accesso inviata" if sent else "Invio email non riuscito", email_sent=sent)


@router.delete("/{member_id}", response_model=MessageOut)
async def delete_member(member_id: str):
    await _get_member(member_id)
    await get_db().users.delete_one({"id": member_id})
    await get_db().auth_tokens.delete_many({"user_id": member_id})
    return MessageOut(message="Socio eliminato")
