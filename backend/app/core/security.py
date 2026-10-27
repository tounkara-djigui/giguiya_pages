from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, Response

from app.core.config import settings
from app.core.database import NO_ID, get_db
from app.core.utils import utcnow

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


async def find_user(user_id: str) -> dict | None:
    return await get_db().users.find_one({"id": user_id}, NO_ID)


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        header = request.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else None
    if not token:
        raise HTTPException(status_code=401, detail="Non autenticato")
    payload = decode_token(token, "access")
    user = await find_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    return user


def is_super_admin(user: dict) -> bool:
    return user.get("role") == "admin" and user.get("email", "").lower() == settings.ADMIN_EMAIL.lower()


def is_approved_admin(user: dict) -> bool:
    return (user.get("role") == "admin" and bool(user.get("email_verified"))
            and (is_super_admin(user) or user.get("admin_status") == "approved"))


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if not is_approved_admin(user):
        raise HTTPException(status_code=403, detail="Accesso riservato agli amministratori")
    return user


async def require_super_admin(user: dict = Depends(require_admin)) -> dict:
    if not is_super_admin(user):
        raise HTTPException(status_code=403, detail="Riservato all'amministratore principale")
    return user


async def require_member(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "member" or not user.get("member"):
        raise HTTPException(status_code=403, detail="Accesso riservato ai soci")
    return user
