from fastapi import APIRouter, HTTPException

from app.core.database import NO_ID, get_db
from app.core.utils import new_id, utcnow
from app.routers.projects import PROJECT_SORT
from app.schemas.auth import MessageOut
from app.schemas.project import ProjectIn, ProjectOut
from app.services.event_service import unique_slug

router = APIRouter(prefix="/projects")


async def _get_project(project_id: str) -> dict:
    project = await get_db().projects.find_one({"id": project_id}, NO_ID)
    if not project:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    return project


@router.get("", response_model=list[ProjectOut])
async def list_projects():
    return await get_db().projects.find({}, NO_ID).sort(PROJECT_SORT).to_list(500)


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(data: ProjectIn):
    project = {**data.model_dump(), "id": new_id(), "slug": await unique_slug(get_db().projects, data.title),
               "created_at": utcnow()}
    await get_db().projects.insert_one(dict(project))
    return project


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: str, data: ProjectIn):
    project = await _get_project(project_id)
    values = data.model_dump()
    if data.title != project["title"]:
        values["slug"] = await unique_slug(get_db().projects, data.title, exclude_id=project_id)
    await get_db().projects.update_one({"id": project_id}, {"$set": values})
    return await _get_project(project_id)


@router.delete("/{project_id}", response_model=MessageOut)
async def delete_project(project_id: str):
    await _get_project(project_id)
    await get_db().projects.delete_one({"id": project_id})
    return MessageOut(message="Progetto eliminato")
