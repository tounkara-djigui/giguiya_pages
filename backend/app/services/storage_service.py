import asyncio
import logging
import os

import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)

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
    try:
        _init_storage()
        logger.info("Object storage initialized")
    except Exception as e:
        logger.error(f"Object storage init failed: {e}")


async def put_object(path: str, data: bytes, content_type: str) -> dict:
    try:
        resp = await asyncio.to_thread(_request, "PUT", path, data=data, headers={"Content-Type": content_type})
    except requests.RequestException as e:
        logger.error(f"Storage upload failed: {e}")
        raise HTTPException(status_code=502, detail="Caricamento file non riuscito")
    return resp.json()


async def get_object(path: str) -> bytes:
    try:
        resp = await asyncio.to_thread(_request, "GET", path)
    except requests.RequestException:
        raise HTTPException(status_code=404, detail="File non trovato")
    return resp.content
