from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_db
from app.core.utils import slugify, to_local_str, utcnow
from app.schemas.event import EventOut


async def unique_slug(collection: AsyncIOMotorCollection, title: str, exclude_id: str | None = None) -> str:
    base = slugify(title)
    slug, i = base, 2
    while True:
        query = {"slug": slug}
        if exclude_id:
            query["id"] = {"$ne": exclude_id}
        if not await collection.find_one(query, {"_id": 1}):
            return slug
        slug, i = f"{base}-{i}", i + 1


async def booking_counts(event_ids: list[str]) -> dict[str, int]:
    if not event_ids:
        return {}
    rows = get_db().bookings.aggregate([
        {"$match": {"event_id": {"$in": event_ids}}},
        {"$group": {"_id": "$event_id", "n": {"$sum": 1}}},
    ])
    return {r["_id"]: r["n"] async for r in rows}


def event_out(e: dict, count: int = 0) -> EventOut:
    capacity = e.get("capacity")
    return EventOut(
        **{k: v for k, v in e.items() if k != "_id"},
        bookings_count=count, spots_left=(max(capacity - count, 0) if capacity else None),
        start_local=to_local_str(e["start_at"]), end_local=to_local_str(e.get("end_at")),
        is_past=(e.get("end_at") or e["start_at"]) < utcnow(),
    )


async def events_out(events: list[dict]) -> list[EventOut]:
    counts = await booking_counts([e["id"] for e in events])
    return [event_out(e, counts.get(e["id"], 0)) for e in events]


async def event_titles(event_ids: list[str]) -> dict[str, dict]:
    cursor = get_db().events.find({"id": {"$in": list(set(event_ids))}}, {"_id": 0, "id": 1, "title": 1, "slug": 1, "start_at": 1})
    return {e["id"]: e async for e in cursor}
