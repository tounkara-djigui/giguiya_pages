from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (clear_auth_cookies, decode_token, get_current_user, hash_password,
                               set_access_cookie, set_auth_cookies, verify_password)
from app.core.utils import utcnow
from app.models import LoginAttempt, User
from app.schemas.auth import (AdminRegisterIn, ChangePasswordIn, EmailIn, LoginIn, MessageOut,
                              SetPasswordIn, TokenIn, UserOut)
from app.services import email_templates as tpl
from app.services.email_service import try_send_email
from app.services.token_service import consume_token, issue_token

router = APIRouter(prefix="/auth", tags=["auth"])

MAX_ATTEMPTS = 5
LOCK_MINUTES = 15


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown")


async def _register_failure(db: AsyncSession, attempt: LoginAttempt | None, identifier: str) -> None:
    if attempt is None:
        attempt = LoginAttempt(identifier=identifier, count=0)
        db.add(attempt)
    attempt.count += 1
    if attempt.count >= MAX_ATTEMPTS:
        attempt.locked_until = utcnow() + timedelta(minutes=LOCK_MINUTES)
        attempt.count = 0
    await db.commit()


@router.post("/login", response_model=UserOut)
async def login(data: LoginIn, request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    email = data.email.lower()
    identifier = f"{_client_ip(request)}:{email}"
    attempt = await db.get(LoginAttempt, identifier)
    if attempt and attempt.locked_until and attempt.locked_until > utcnow():
        raise HTTPException(status_code=429, detail="Troppi tentativi. Riprova tra 15 minuti.")
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        await _register_failure(db, attempt, identifier)
        if user and not user.password_hash:
            raise HTTPException(status_code=401, detail="Password non ancora impostata: usa il link ricevuto via email")
        raise HTTPException(status_code=401, detail="Email o password non corretti")
    if user.role == "admin" and not user.email_verified:
        raise HTTPException(status_code=403, detail="Conferma prima il tuo indirizzo email tramite il link ricevuto")
    if attempt:
        await db.delete(attempt)
        await db.commit()
    set_auth_cookies(response, user.id)
    return user


@router.post("/logout", response_model=MessageOut)
async def logout(response: Response):
    clear_auth_cookies(response)
    return MessageOut(message="Logout effettuato")


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.post("/refresh", response_model=UserOut)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non autenticato")
    payload = decode_token(token, "refresh")
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    set_access_cookie(response, user.id)
    return user


@router.post("/admin/register", response_model=MessageOut)
async def admin_register(data: AdminRegisterIn, db: AsyncSession = Depends(get_db)):
    email = data.email.lower()
    if not email.endswith("@" + settings.ADMIN_EMAIL_DOMAIN):
        raise HTTPException(status_code=400, detail=f"Solo indirizzi @{settings.ADMIN_EMAIL_DOMAIN} possono registrarsi come amministratori")
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if user and (user.role != "admin" or user.email_verified):
        raise HTTPException(status_code=409, detail="Esiste già un account con questa email")
    if not user:
        user = User(email=email, role="admin", email_verified=False, first_name="", last_name="")
        db.add(user)
    user.first_name, user.last_name = data.first_name.strip(), data.last_name.strip()
    user.password_hash = hash_password(data.password)
    await db.flush()
    raw = await issue_token(db, user.id, "verify_email", hours=48)
    await db.commit()
    subject, html = tpl.admin_verification(user.first_name, raw)
    sent = await try_send_email(to=email, subject=subject, html=html)
    return MessageOut(message="Account creato. Controlla la tua email per confermarlo.", email_sent=sent)


@router.post("/verify-email", response_model=MessageOut)
async def verify_email(data: TokenIn, db: AsyncSession = Depends(get_db)):
    token = await consume_token(db, data.token, ("verify_email",))
    user = await db.get(User, token.user_id)
    user.email_verified = True
    await db.commit()
    return MessageOut(message="Email confermata. Ora puoi accedere.")


@router.post("/set-password", response_model=MessageOut)
async def set_password(data: SetPasswordIn, db: AsyncSession = Depends(get_db)):
    token = await consume_token(db, data.token, ("set_password", "reset_password"))
    user = await db.get(User, token.user_id)
    user.password_hash = hash_password(data.password)
    if user.role == "member":
        user.email_verified = True
    await db.commit()
    return MessageOut(message="Password impostata. Ora puoi accedere.")


@router.post("/forgot-password", response_model=MessageOut)
async def forgot_password(data: EmailIn, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == data.email.lower()))).scalar_one_or_none()
    if user:
        raw = await issue_token(db, user.id, "reset_password", hours=1)
        await db.commit()
        subject, html = tpl.password_reset(user.first_name, raw)
        await try_send_email(to=user.email, subject=subject, html=html)
    return MessageOut(message="Se l'email è registrata, riceverai un link per reimpostare la password.")


@router.post("/change-password", response_model=MessageOut)
async def change_password(data: ChangePasswordIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Password attuale non corretta")
    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return MessageOut(message="Password aggiornata")
