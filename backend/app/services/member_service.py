from app.core.config import settings
from app.core.utils import current_year
from app.models import Member
from app.schemas.member import FeeOut, MemberOut


def member_out(member: Member) -> MemberOut:
    year = current_year()
    paid_years = {f.year for f in member.fees}
    current_paid = year in paid_years
    u = member.user
    return MemberOut(
        id=member.id, user_id=u.id, email=u.email, first_name=u.first_name, last_name=u.last_name,
        phone=u.phone, membership_number=member.membership_number, birth_date=member.birth_date,
        birth_place=member.birth_place, fiscal_code=member.fiscal_code, address=member.address,
        city=member.city, enrollment_paid=member.enrollment_paid, enrollment_paid_at=member.enrollment_paid_at,
        card_issued=member.card_issued, card_issued_at=member.card_issued_at, notes=member.notes,
        created_at=member.created_at, account_active=bool(u.password_hash),
        fees=[FeeOut(year=f.year, amount=f.amount, paid_at=f.paid_at) for f in member.fees],
        current_year=year, current_year_paid=current_paid,
        in_good_standing=member.enrollment_paid and current_paid,
        enrollment_fee=settings.ENROLLMENT_FEE, annual_fee=settings.ANNUAL_FEE,
    )
