import secrets
from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import sha256, utcnow
from app.models import AuthToken


async def issue_token(db: AsyncSession, user_id: str, purpose: str, hours: int) -> str:
    raw = secrets.token_urlsafe(32)
    db.add(AuthToken(token_hash=sha256(raw), user_id=user_id, purpose=purpose,
                     expires_at=utcnow() + timedelta(hours=hours)))
    return raw


async def consume_token(db: AsyncSession, raw: str, purposes: tuple[str, ...]) -> AuthToken:
    token = (await db.execute(select(AuthToken).where(AuthToken.token_hash == sha256(raw)))).scalar_one_or_none()
    if not token or token.purpose not in purposes or token.used_at or token.expires_at < utcnow():
        raise HTTPException(status_code=400, detail="Link non valido o scaduto")
    token.used_at = utcnow()
    return token
