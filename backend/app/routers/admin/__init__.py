from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.routers.admin import contacts, events, members, projects, staff, stats

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])
for module in (stats, members, contacts, events, projects, staff):
    router.include_router(module.router)
