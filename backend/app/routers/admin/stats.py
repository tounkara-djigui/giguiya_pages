from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.utils import current_year, utcnow
from app.models import Booking, Event, Member, Project
from app.schemas.admin import StatsOut
from app.services.member_service import member_out

router = APIRouter()


async def _count(db: AsyncSession, q) -> int:
    return (await db.execute(q)).scalar_one()


@router.get("/stats", response_model=StatsOut)
async def stats(db: AsyncSession = Depends(get_db)):
    members = [member_out(m) for m in (await db.execute(select(Member))).scalars().all()]
    return StatsOut(
        members_total=len(members),
        members_in_good_standing=sum(m.in_good_standing for m in members),
        members_pending_card=sum(not m.card_issued for m in members),
        members_pending_enrollment=sum(not m.enrollment_paid for m in members),
        bookings_total=await _count(db, select(func.count()).select_from(Booking)),
        contacts_total=await _count(db, select(func.count(func.distinct(Booking.email)))),
        upcoming_events=await _count(db, select(func.count()).select_from(Event).where(Event.start_at >= utcnow())),
        projects_total=await _count(db, select(func.count()).select_from(Project)),
        current_year=current_year(),
    )
