import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile

from app.core.database import get_db
from app.core.security import require_admin
from app.core.utils import new_id, utcnow
from app.services.storage_service import APP_NAME, get_object, put_object

router = APIRouter(tags=["files"])

IMAGE_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif"}
MAX_BYTES = 8 * 1024 * 1024


@router.post("/admin/uploads", status_code=201)
async def upload_image(file: UploadFile = File(...), admin: dict = Depends(require_admin)):
    ext = IMAGE_TYPES.get(file.content_type or "")
    if not ext:
        raise HTTPException(status_code=400, detail="Formato non supportato: usa JPG, PNG, WEBP o GIF")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Immagine troppo grande (massimo 8 MB)")
    result = await put_object(f"{APP_NAME}/images/{uuid.uuid4()}.{ext}", data, file.content_type)
    await get_db().files.insert_one({
        "id": new_id(), "storage_path": result["path"], "original_filename": file.filename,
        "content_type": file.content_type, "size": result.get("size", len(data)), "uploaded_by": admin["id"],
        "is_deleted": False, "created_at": utcnow(),
    })
    return {"url": f"/api/files/{result['path']}", "path": result["path"]}


@router.get("/files/{path:path}")
async def serve_file(path: str):
    record = await get_db().files.find_one({"storage_path": path, "is_deleted": False})
    if not record:
        raise HTTPException(status_code=404, detail="File non trovato")
    data = await get_object(path)
    return Response(content=data, media_type=record["content_type"], headers={"Cache-Control": "public, max-age=86400"})
