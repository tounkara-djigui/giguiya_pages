from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import slugify, to_local_str, utcnow
from app.models import Booking, Event
from app.schemas.event import EventOut


async def unique_slug(db: AsyncSession, model, title: str, exclude_id: str | None = None) -> str:
    base = slugify(title)
    slug, i = base, 2
    while True:
        q = select(model.id).where(model.slug == slug)
        if exclude_id:
            q = q.where(model.id != exclude_id)
        if not (await db.execute(q)).first():
            return slug
        slug, i = f"{base}-{i}", i + 1


async def booking_counts(db: AsyncSession, event_ids: list[str]) -> dict[str, int]:
    if not event_ids:
        return {}
    rows = await db.execute(
        select(Booking.event_id, func.count()).where(Booking.event_id.in_(event_ids)).group_by(Booking.event_id)
    )
    return dict(rows.all())


def event_out(e: Event, count: int = 0) -> EventOut:
    return EventOut(
        id=e.id, slug=e.slug, title=e.title, summary=e.summary, description=e.description,
        category=e.category, location=e.location, start_at=e.start_at, end_at=e.end_at,
        image_url=e.image_url, capacity=e.capacity, price_label=e.price_label, is_published=e.is_published,
        bookings_count=count, spots_left=(max(e.capacity - count, 0) if e.capacity else None),
        start_local=to_local_str(e.start_at), end_local=to_local_str(e.end_at),
        is_past=(e.end_at or e.start_at) < utcnow(),
    )


async def events_out(db: AsyncSession, events: list[Event]) -> list[EventOut]:
    counts = await booking_counts(db, [e.id for e in events])
    return [event_out(e, counts.get(e.id, 0)) for e in events]
