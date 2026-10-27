from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.database import NO_ID, get_db
from app.core.security import require_super_admin
from app.schemas.auth import MessageOut, StaffOut
from app.services import email_templates as tpl
from app.services.email_service import try_send_email

router = APIRouter(prefix="/staff", dependencies=[Depends(require_super_admin)])


def _staff_query(extra: dict | None = None) -> dict:
    return {"role": "admin", "email": {"$ne": settings.ADMIN_EMAIL.lower()}, **(extra or {})}


async def _get_staff(staff_id: str) -> dict:
    user = await get_db().users.find_one(_staff_query({"id": staff_id}), NO_ID)
    if not user:
        raise HTTPException(status_code=404, detail="Account staff non trovato")
    return user


@router.get("", response_model=list[StaffOut])
async def list_staff():
    return await get_db().users.find(_staff_query(), NO_ID).sort("created_at", -1).to_list(500)


@router.post("/{staff_id}/approve", response_model=MessageOut)
async def approve_staff(staff_id: str):
    user = await _get_staff(staff_id)
    if not user.get("email_verified"):
        raise HTTPException(status_code=400, detail="L'utente non ha ancora confermato la sua email")
    await get_db().users.update_one({"id": staff_id}, {"$set": {"admin_status": "approved"}})
    subject, html = tpl.staff_approved(user["first_name"])
    sent = await try_send_email(to=user["email"], subject=subject, html=html)
    return MessageOut(message="Amministratore approvato", email_sent=sent)


@router.post("/{staff_id}/revoke", response_model=MessageOut)
async def revoke_staff(staff_id: str):
    await _get_staff(staff_id)
    await get_db().users.update_one({"id": staff_id}, {"$set": {"admin_status": "pending"}})
    return MessageOut(message="Accesso revocato: l'account è tornato in attesa")


@router.delete("/{staff_id}", response_model=MessageOut)
async def delete_staff(staff_id: str):
    await _get_staff(staff_id)
    await get_db().users.delete_one({"id": staff_id})
    await get_db().auth_tokens.delete_many({"user_id": staff_id})
    return MessageOut(message="Account staff eliminato")
