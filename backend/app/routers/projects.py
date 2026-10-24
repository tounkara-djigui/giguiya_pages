from fastapi import APIRouter, HTTPException

from app.core.database import NO_ID, get_db
from app.schemas.project import ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

PROJECT_SORT = [("sort_order", 1), ("created_at", 1)]


@router.get("", response_model=list[ProjectOut])
async def list_projects():
    return await get_db().projects.find({"is_published": True}, NO_ID).sort(PROJECT_SORT).to_list(200)


@router.get("/{slug}", response_model=ProjectOut)
async def get_project(slug: str):
    project = await get_db().projects.find_one({"$or": [{"slug": slug}, {"id": slug}], "is_published": True}, NO_ID)
    if not project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return project
