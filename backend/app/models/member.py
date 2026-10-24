from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.utils import new_id, utcnow


class Member(Base):
    __tablename__ = "members"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    membership_number: Mapped[str] = mapped_column(String(30), unique=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fiscal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    enrollment_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    enrollment_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    card_issued: Mapped[bool] = mapped_column(Boolean, default=False)
    card_issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped["User"] = relationship(back_populates="member", lazy="selectin")  # noqa: F821
    fees: Mapped[list["MembershipFee"]] = relationship(
        back_populates="member", cascade="all, delete-orphan", lazy="selectin", order_by="MembershipFee.year.desc()"
    )


class MembershipFee(Base):
    __tablename__ = "membership_fees"
    __table_args__ = (UniqueConstraint("member_id", "year"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    member_id: Mapped[str] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(Integer)
    paid_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    member: Mapped["Member"] = relationship(back_populates="fees")
