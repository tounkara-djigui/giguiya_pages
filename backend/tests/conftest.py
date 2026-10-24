import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values
from pymongo import MongoClient

BACKEND_ENV = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
FRONTEND_ENV = dotenv_values(Path(__file__).resolve().parents[2] / "frontend" / ".env")
BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or FRONTEND_ENV["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_EMAIL = BACKEND_ENV["ADMIN_EMAIL"]
ADMIN_PASSWORD = BACKEND_ENV["ADMIN_PASSWORD"]
ADMIN_DOMAIN = BACKEND_ENV.get("ADMIN_EMAIL_DOMAIN", "giguiya.it")

_mongo = MongoClient(BACKEND_ENV["MONGO_URL"], tz_aware=True)
DB = _mongo[BACKEND_ENV["DB_NAME"]]


def make_email(tag: str) -> str:
    return f"test_{tag}_{uuid.uuid4().hex[:8]}@example.com"


def insert_token(user_id: str, purpose: str) -> str:
    raw = uuid.uuid4().hex + uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    DB.auth_tokens.insert_one({"id": str(uuid.uuid4()), "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
                               "user_id": user_id, "purpose": purpose, "expires_at": now + timedelta(hours=1),
                               "used_at": None, "created_at": now})
    return raw


def future_local(days: int = 10, hour: int = 18) -> str:
    return (datetime.now() + timedelta(days=days)).replace(hour=hour, minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")


@pytest.fixture(scope="session")
def admin_client():
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    if r.status_code != 200:
        pytest.skip(f"Admin login failed {r.status_code} {r.text}")
    return s


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    rx = {"$regex": r"^test_.*@(example\.com|giguiya\.it)$", "$options": "i"}
    users = list(DB.users.find({"email": rx}, {"id": 1}))
    ids = [u["id"] for u in users]
    DB.auth_tokens.delete_many({"user_id": {"$in": ids}})
    DB.users.delete_many({"id": {"$in": ids}})
    test_events = [e["id"] for e in DB.events.find({"title": {"$regex": "^TEST_"}}, {"id": 1})]
    DB.bookings.delete_many({"$or": [{"email": rx}, {"event_id": {"$in": test_events}}]})
    DB.events.delete_many({"id": {"$in": test_events}})
    DB.projects.delete_many({"title": {"$regex": "^TEST_"}})
    DB.login_attempts.delete_many({"identifier": {"$regex": "test_|" + ADMIN_EMAIL.replace(".", r"\.")}})
    admin = DB.users.find_one({"email": ADMIN_EMAIL}, {"id": 1})
    if admin:
        DB.files.update_many({"uploaded_by": admin["id"], "original_filename": {"$regex": "^test_"}},
                             {"$set": {"is_deleted": True}})
