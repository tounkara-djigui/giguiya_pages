import asyncio
import logging
import os

import requests
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from app.core.database import db

logger = logging.getLogger(__name__)

USE_EMERGENT = bool(os.environ.get("EMERGENT_LLM_KEY"))
_grid: AsyncIOMotorGridFSBucket | None = None


def _bucket() -> AsyncIOMotorGridFSBucket:
    global _grid
    if _grid is None:
        _grid = AsyncIOMotorGridFSBucket(db, bucket_name="uploads")
    return _grid

STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
APP_NAME = "giguiya"
_storage_key: str | None = None


def _init_storage(force: bool = False) -> str:
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": os.environ["EMERGENT_LLM_KEY"]}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key


def _request(method: str, path: str, **kwargs) -> requests.Response:
    for force in (False, True):
        headers = {"X-Storage-Key": _init_storage(force), **kwargs.pop("headers", {})}
        resp = requests.request(method, f"{STORAGE_URL}/objects/{path}", headers=headers, timeout=120, **kwargs)
        if resp.status_code != 404 or force or method == "GET":
            break
    resp.raise_for_status()
    return resp


def init_storage() -> None:
    if not USE_EMERGENT:
        logger.info("Object storage: MongoDB GridFS")
        return
    try:
        _init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.error(f"Object storage init failed: {e}")


async def put_object(path: str, data: bytes, content_type: str) -> dict:
    if not USE_EMERGENT:
        await _bucket().upload_from_stream(path, data, metadata={"contentType": content_type})
        return {"path": path, "size": len(data)}
    try:
        resp = await asyncio.to_thread(_request, "PUT", path, data=data, headers={"Content-Type": content_type})
    except requests.RequestException as e:
        logger.error(f"Storage upload failed: {e}")
        raise HTTPException(status_code=502, detail="Caricamento file non riuscito")
    return resp.json()


async def get_object(path: str) -> bytes:
    if not USE_EMERGENT:
        found = await _bucket().find({"filename": path}, limit=1).to_list(1)
        if not found:
            raise HTTPException(status_code=404, detail="File non trovato")
        stream = await _bucket().open_download_stream(found[0]["_id"])
        return await stream.read()
    try:
        resp = await asyncio.to_thread(_request, "GET", path)
    except requests.RequestException:
        raise HTTPException(status_code=404, detail="File non trovato")
    return resp.content
