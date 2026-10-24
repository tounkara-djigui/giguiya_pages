import hashlib
import re
import unicodedata
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.core.config import settings

TZ = ZoneInfo(settings.TIMEZONE)


def new_id() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:80] or "item"


def localize(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.replace(tzinfo=TZ) if dt.tzinfo is None else dt


def to_local_str(dt: datetime | None) -> str | None:
    return dt.astimezone(TZ).strftime("%Y-%m-%dT%H:%M") if dt else None


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def current_year() -> int:
    return datetime.now(TZ).year
