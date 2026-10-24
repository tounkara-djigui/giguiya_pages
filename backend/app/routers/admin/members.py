from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.utils import utcnow
from app.models import Member, MembershipFee, User
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


async def _get_member(db: AsyncSession, member_id: str) -> Member:
    member = await db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Socio non trovato")
    return member


@router.get("", response_model=list[MemberOut])
async def list_members(q: str | None = None, status: str = Query("all"), db: AsyncSession = Depends(get_db)):
    query = select(Member).join(User).order_by(User.last_name, User.first_name)
    if q:
        like = f"%{q.strip()}%"
        query = query.where(or_(User.first_name.ilike(like), User.last_name.ilike(like),
                                User.email.ilike(like), Member.membership_number.ilike(like)))
    members = [member_out(m) for m in (await db.execute(query)).scalars().all()]
    if status in STATUS_FILTERS:
        members = [m for m in members if STATUS_FILTERS[status](m)]
    return members


@router.get("/{member_id}", response_model=MemberOut)
async def get_member(member_id: str, db: AsyncSession = Depends(get_db)):
    return member_out(await _get_member(db, member_id))


@router.patch("/{member_id}", response_model=MemberOut)
async def update_member(member_id: str, data: MemberUpdateIn, db: AsyncSession = Depends(get_db)):
    member = await _get_member(db, member_id)
    changes = data.model_dump(exclude_unset=True)
    if "enrollment_paid" in changes:
        member.enrollment_paid = changes["enrollment_paid"]
        member.enrollment_paid_at = utcnow() if member.enrollment_paid else None
    if "card_issued" in changes:
        member.card_issued = changes["card_issued"]
        member.card_issued_at = utcnow() if member.card_issued else None
    for field in ("notes", "address", "city"):
        if field in changes:
            setattr(member, field, changes[field])
    if "phone" in changes:
        member.user.phone = changes["phone"]
    await db.commit()
    await db.refresh(member)
    return member_out(member)


@router.put("/{member_id}/fees/{year}", response_model=MemberOut)
async def toggle_fee(member_id: str, year: int, data: FeeToggleIn, db: AsyncSession = Depends(get_db)):
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Anno non valido")
    member = await _get_member(db, member_id)
    existing = next((f for f in member.fees if f.year == year), None)
    if data.paid and not existing:
        member.fees.append(MembershipFee(year=year, amount=settings.ANNUAL_FEE))
    elif not data.paid and existing:
        member.fees.remove(existing)
    await db.commit()
    await db.refresh(member)
    return member_out(member)


@router.post("/{member_id}/resend-invite", response_model=MessageOut)
async def resend_invite(member_id: str, db: AsyncSession = Depends(get_db)):
    member = await _get_member(db, member_id)
    sent = await send_member_invite(db, member.user, member.membership_number)
    return MessageOut(message="Email di accesso inviata" if sent else "Invio email non riuscito", email_sent=sent)


@router.delete("/{member_id}", response_model=MessageOut)
async def delete_member(member_id: str, db: AsyncSession = Depends(get_db)):
    member = await _get_member(db, member_id)
    await db.delete(member.user)
    await db.commit()
    return MessageOut(message="Socio eliminato")
