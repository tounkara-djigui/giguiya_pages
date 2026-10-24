from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.routers.admin import contacts, events, members, projects, stats

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
for module in (stats, members, contacts, events, projects):
    router.include_router(module.router)
