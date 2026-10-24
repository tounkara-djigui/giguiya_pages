from fastapi import APIRouter

from app.core.database import NO_ID, get_db
from app.core.utils import current_year, utcnow
from app.schemas.admin import StatsOut
from app.services.member_service import member_out

router = APIRouter()


@router.get("/stats", response_model=StatsOut)
async def stats():
    db = get_db()
    members = [member_out(u) for u in await db.users.find({"role": "member"}, NO_ID).to_list(10000)]
    return StatsOut(
        members_total=len(members),
        members_in_good_standing=sum(m.in_good_standing for m in members),
        members_pending_card=sum(not m.card_issued for m in members),
        members_pending_enrollment=sum(not m.enrollment_paid for m in members),
        bookings_total=await db.bookings.count_documents({}),
        contacts_total=len(await db.bookings.distinct("email")),
        upcoming_events=await db.events.count_documents({"start_at": {"$gte": utcnow()}}),
        projects_total=await db.projects.count_documents({}),
        current_year=current_year(),
    )
