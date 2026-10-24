from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.utils import new_id, utcnow


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    subtitle: Mapped[str] = mapped_column(String(300), default="")
    category: Mapped[str] = mapped_column(String(60), default="Comunità")
    summary: Mapped[str] = mapped_column(String(600), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    partners: Mapped[str] = mapped_column(String(300), default="")
    year_label: Mapped[str] = mapped_column(String(40), default="")
    highlights: Mapped[list] = mapped_column(JSON, default=list)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
