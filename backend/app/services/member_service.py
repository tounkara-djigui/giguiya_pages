from app.core.config import settings
from app.core.utils import current_year
from app.schemas.member import FeeOut, MemberOut


def member_out(user: dict) -> MemberOut:
    m = user["member"]
    year = current_year()
    fees = sorted(m.get("fees", []), key=lambda f: f["year"], reverse=True)
    current_paid = any(f["year"] == year for f in fees)
    return MemberOut(
        id=user["id"], user_id=user["id"], email=user["email"], first_name=user["first_name"],
        last_name=user["last_name"], phone=user.get("phone"), membership_number=m["membership_number"],
        birth_date=m.get("birth_date"), birth_place=m.get("birth_place"), fiscal_code=m.get("fiscal_code"),
        address=m.get("address"), city=m.get("city"), enrollment_paid=m.get("enrollment_paid", False),
        enrollment_paid_at=m.get("enrollment_paid_at"), card_issued=m.get("card_issued", False),
        card_issued_at=m.get("card_issued_at"), notes=m.get("notes"), created_at=user["created_at"],
        account_active=bool(user.get("password_hash")),
        fees=[FeeOut(**f) for f in fees], current_year=year, current_year_paid=current_paid,
        in_good_standing=m.get("enrollment_paid", False) and current_paid,
        enrollment_fee=settings.ENROLLMENT_FEE, annual_fee=settings.ANNUAL_FEE,
    )
