from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_member
from app.core.utils import current_year
from app.models import Booking, Member, User
from app.schemas.auth import MessageOut
from app.schemas.member import MemberBookingOut, MemberDashboardOut, MemberRegisterIn
from app.services import email_templates as tpl
from app.services.email_service import try_send_email
from app.services.member_service import member_out
from app.services.token_service import issue_token

router = APIRouter(prefix="/members", tags=["members"])


async def next_membership_number(db: AsyncSession) -> str:
    prefix = f"GIG-{current_year()}-"
    last = (await db.execute(
        select(Member.membership_number).where(Member.membership_number.like(f"{prefix}%"))
        .order_by(Member.membership_number.desc()).limit(1)
    )).scalar_one_or_none()
    seq = int(last.rsplit("-", 1)[1]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


async def send_member_invite(db: AsyncSession, user: User, number: str) -> bool:
    raw = await issue_token(db, user.id, "set_password", hours=24 * 7)
    await db.commit()
    subject, html = tpl.member_welcome(user.first_name, number, raw)
    return await try_send_email(to=user.email, subject=subject, html=html)


@router.post("/register", response_model=MessageOut, status_code=201)
async def register_member(data: MemberRegisterIn, db: AsyncSession = Depends(get_db)):
    email = data.email.lower()
    if (await db.execute(select(User.id).where(User.email == email))).first():
        raise HTTPException(status_code=409, detail="Esiste già un account con questa email")
    user = User(email=email, role="member", first_name=data.first_name.strip(),
                last_name=data.last_name.strip(), phone=data.phone or None)
    number = await next_membership_number(db)
    user.member = Member(
        membership_number=number, birth_date=data.birth_date, birth_place=data.birth_place,
        fiscal_code=(data.fiscal_code or "").upper() or None, address=data.address, city=data.city,
    )
    db.add(user)
    await db.flush()
    sent = await send_member_invite(db, user, number)
    return MessageOut(message="Domanda di iscrizione ricevuta! Controlla la tua email.", email_sent=sent)


@router.get("/me", response_model=MemberDashboardOut)
async def my_membership(user: User = Depends(require_member), db: AsyncSession = Depends(get_db)):
    bookings = (await db.execute(
        select(Booking).where(Booking.email == user.email).order_by(Booking.created_at.desc())
    )).scalars().all()
    return MemberDashboardOut(
        member=member_out(user.member),
        bookings=[MemberBookingOut(id=b.id, event_title=b.event.title, event_slug=b.event.slug,
                                   event_start=b.event.start_at, created_at=b.created_at) for b in bookings],
    )
