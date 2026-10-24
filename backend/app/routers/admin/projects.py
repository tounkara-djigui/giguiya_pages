from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Project
from app.schemas.auth import MessageOut
from app.schemas.project import ProjectIn, ProjectOut
from app.services.event_service import unique_slug

router = APIRouter(prefix="/projects")


async def _get_project(db: AsyncSession, project_id: str) -> Project:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return project


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Project).order_by(Project.sort_order, Project.created_at))).scalars().all()


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(data: ProjectIn, db: AsyncSession = Depends(get_db)):
    project = Project(slug=await unique_slug(db, Project, data.title), **data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: str, data: ProjectIn, db: AsyncSession = Depends(get_db)):
    project = await _get_project(db, project_id)
    if data.title != project.title:
        project.slug = await unique_slug(db, Project, data.title, exclude_id=project.id)
    for k, v in data.model_dump().items():
        setattr(project, k, v)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", response_model=MessageOut)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    await db.delete(await _get_project(db, project_id))
    await db.commit()
    return MessageOut(message="Progetto eliminato")
