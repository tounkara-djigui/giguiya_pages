from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL, tz_aware=True)
db: AsyncIOMotorDatabase = client[settings.DB_NAME]

NO_ID = {"_id": 0}


def get_db() -> AsyncIOMotorDatabase:
    return db


async def init_indexes() -> None:
    await db.users.create_index("id", unique=True)
    await db.users.create_index("email", unique=True)
    await db.users.create_index(
        "member.membership_number", unique=True,
        partialFilterExpression={"member.membership_number": {"$exists": True}},
    )
    for name in ("events", "projects"):
        await db[name].create_index("id", unique=True)
        await db[name].create_index("slug", unique=True)
    await db.events.create_index("start_at")
    await db.bookings.create_index("id", unique=True)
    await db.bookings.create_index([("event_id", 1), ("email", 1)], unique=True)
    await db.bookings.create_index("email")
    await db.auth_tokens.create_index("token_hash", unique=True)
    await db.login_attempts.create_index("identifier", unique=True)
