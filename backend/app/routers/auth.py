from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.core.config import settings
from app.core.database import NO_ID, get_db
from app.core.security import (clear_auth_cookies, decode_token, find_user, get_current_user, hash_password,
                               set_access_cookie, set_auth_cookies, verify_password)
from app.core.utils import new_id, utcnow
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
    return fwd.split(",")[-1].strip() if fwd else (request.client.host if request.client else "unknown")


async def _register_failure(attempt: dict | None, identifier: str) -> None:
    count = (attempt or {}).get("count", 0) + 1
    update = {"count": count}
    if count >= MAX_ATTEMPTS:
        update = {"count": 0, "locked_until": utcnow() + timedelta(minutes=LOCK_MINUTES)}
    await get_db().login_attempts.update_one({"identifier": identifier}, {"$set": update}, upsert=True)


def _ensure_not_locked(attempt: dict | None) -> None:
    if attempt and attempt.get("locked_until") and attempt["locked_until"] > utcnow():
        raise HTTPException(status_code=429, detail="Troppi tentativi. Riprova tra 15 minuti.")


async def _authenticate(email: str, password: str, attempt: dict | None, identifier: str) -> dict:
    user = await get_db().users.find_one({"email": email}, NO_ID)
    if user and verify_password(password, user.get("password_hash")):
        return user
    await _register_failure(attempt, identifier)
    if user and not user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Password non ancora impostata: usa il link ricevuto via email")
    raise HTTPException(status_code=401, detail="Email o password non corretti")


@router.post("/login", response_model=UserOut)
async def login(data: LoginIn, request: Request, response: Response):
    email = data.email.lower()
    identifier = f"{_client_ip(request)}:{email}"
    attempt = await get_db().login_attempts.find_one({"identifier": identifier})
    _ensure_not_locked(attempt)
    user = await _authenticate(email, data.password, attempt, identifier)
    if user["role"] == "admin" and not user.get("email_verified"):
        raise HTTPException(status_code=403, detail="Conferma prima il tuo indirizzo email tramite il link ricevuto")
    if attempt:
        await get_db().login_attempts.delete_one({"identifier": identifier})
    set_auth_cookies(response, user["id"])
    return user


@router.post("/logout", response_model=MessageOut)
async def logout(response: Response):
    clear_auth_cookies(response)
    return MessageOut(message="Logout effettuato")


@router.get("/me", response_model=UserOut)
async def me(user: dict = Depends(get_current_user)):
    return user


@router.post("/refresh", response_model=UserOut)
async def refresh(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non autenticato")
    user = await find_user(decode_token(token, "refresh")["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Utente non trovato")
    set_access_cookie(response, user["id"])
    return user


@router.post("/admin/register", response_model=MessageOut)
async def admin_register(data: AdminRegisterIn):
    email = data.email.lower()
    if not email.endswith("@" + settings.ADMIN_EMAIL_DOMAIN):
        raise HTTPException(status_code=400, detail=f"Solo indirizzi @{settings.ADMIN_EMAIL_DOMAIN} possono registrarsi come amministratori")
    user = await get_db().users.find_one({"email": email}, NO_ID)
    if user and (user["role"] != "admin" or user.get("email_verified")):
        raise HTTPException(status_code=409, detail="Esiste già un account con questa email")
    if not user:
        user = {"id": new_id(), "email": email, "role": "admin", "email_verified": False,
                "first_name": data.first_name.strip(), "last_name": data.last_name.strip(), "phone": None,
                "password_hash": hash_password(data.password), "created_at": utcnow()}
        await get_db().users.insert_one(dict(user))
    raw = await issue_token(user["id"], "verify_email", hours=48)
    subject, html = tpl.admin_verification(user["first_name"], raw)
    sent = await try_send_email(to=email, subject=subject, html=html)
    return MessageOut(message="Account creato. Controlla la tua email per confermarlo.", email_sent=sent)


@router.post("/verify-email", response_model=MessageOut)
async def verify_email(data: TokenIn):
    token = await consume_token(data.token, ("verify_email",))
    await get_db().users.update_one({"id": token["user_id"]}, {"$set": {"email_verified": True}})
    return MessageOut(message="Email confermata. Ora puoi accedere.")


@router.post("/set-password", response_model=MessageOut)
async def set_password(data: SetPasswordIn):
    token = await consume_token(data.token, ("set_password", "reset_password"))
    user = await find_user(token["user_id"])
    if not user:
        raise HTTPException(status_code=400, detail="Link non valido o scaduto")
    update = {"password_hash": hash_password(data.password)}
    if user["role"] == "member":
        update["email_verified"] = True
    await get_db().users.update_one({"id": user["id"]}, {"$set": update})
    return MessageOut(message="Password impostata. Ora puoi accedere.")


@router.post("/forgot-password", response_model=MessageOut)
async def forgot_password(data: EmailIn):
    user = await get_db().users.find_one({"email": data.email.lower()}, NO_ID)
    if user:
        raw = await issue_token(user["id"], "reset_password", hours=1)
        subject, html = tpl.password_reset(user["first_name"], raw)
        await try_send_email(to=user["email"], subject=subject, html=html)
    return MessageOut(message="Se l'email è registrata, riceverai un link per reimpostare la password.")


@router.post("/change-password", response_model=MessageOut)
async def change_password(data: ChangePasswordIn, user: dict = Depends(get_current_user)):
    if not verify_password(data.current_password, user.get("password_hash")):
        raise HTTPException(status_code=400, detail="Password attuale non corretta")
    await get_db().users.update_one({"id": user["id"]}, {"$set": {"password_hash": hash_password(data.new_password)}})
    return MessageOut(message="Password aggiornata")
