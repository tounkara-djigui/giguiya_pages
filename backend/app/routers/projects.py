from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Project
from app.schemas.project import ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    q = select(Project).where(Project.is_published.is_(True)).order_by(Project.sort_order, Project.created_at)
    return (await db.execute(q)).scalars().all()


@router.get("/{slug}", response_model=ProjectOut)
async def get_project(slug: str, db: AsyncSession = Depends(get_db)):
    project = (await db.execute(
        select(Project).where(or_(Project.slug == slug, Project.id == slug), Project.is_published.is_(True))
    )).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return project
