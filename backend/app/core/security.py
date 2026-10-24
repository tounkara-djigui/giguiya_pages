from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.utils import utcnow
from app.models import User

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _encode(user_id: str, kind: str, expires: datetime) -> str:
    return jwt.encode({"sub": user_id, "type": kind, "exp": expires}, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str, kind: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessione scaduta")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token non valido")
    else:
        if payload.get("type") != kind:
            raise HTTPException(status_code=401, detail="Token non valido")
        return payload


def _cookie(response: Response, key: str, value: str, max_age: int) -> None:
    response.set_cookie(key=key, value=value, httponly=True, secure=True, samesite="none", max_age=max_age, path="/")


def set_access_cookie(response: Response, user_id: str) -> None:
    minutes = settings.ACCESS_TOKEN_MINUTES
    _cookie(response, "access_token", _encode(user_id, "access", utcnow() + timedelta(minutes=minutes)), minutes * 60)


def set_auth_cookies(response: Response, user_id: str) -> None:
    set_access_cookie(response, user_id)
    days = settings.REFRESH_TOKEN_DAYS
    _cookie(response, "refresh_token", _encode(user_id, "refresh", utcnow() + timedelta(days=days)), days * 86400)


def clear_auth_cookies(response: Response) -> None:
    for key in ("access_token", "refresh_token"):
        response.delete_cookie(key, path="/", secure=True, samesite="none", httponly=True)


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        header = request.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else None
    if not token:
        raise HTTPException(status_code=401, detail="Non autenticato")
    payload = decode_token(token, "access")
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin" or not user.email_verified:
        raise HTTPException(status_code=403, detail="Accesso riservato agli amministratori")
    return user


async def require_member(user: User = Depends(get_current_user)) -> User:
    if user.role != "member" or not user.member:
        raise HTTPException(status_code=403, detail="Accesso riservato ai soci")
    return user
