import secrets
from datetime import timedelta

from fastapi import HTTPException

from app.core.database import get_db
from app.core.utils import new_id, sha256, utcnow


async def issue_token(user_id: str, purpose: str, hours: int) -> str:
    raw = secrets.token_urlsafe(32)
    await get_db().auth_tokens.insert_one({
        "id": new_id(), "token_hash": sha256(raw), "user_id": user_id, "purpose": purpose,
        "expires_at": utcnow() + timedelta(hours=hours), "used_at": None, "created_at": utcnow(),
    })
    return raw


async def consume_token(raw: str, purposes: tuple[str, ...]) -> dict:
    token = await get_db().auth_tokens.find_one_and_update(
        {"token_hash": sha256(raw), "purpose": {"$in": list(purposes)}, "used_at": None,
         "expires_at": {"$gt": utcnow()}},
        {"$set": {"used_at": utcnow()}},
    )
    if not token:
        raise HTTPException(status_code=400, detail="Link non valido o scaduto")
    return token
