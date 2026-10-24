import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    DATABASE_URL = os.environ["DATABASE_URL"]
    JWT_SECRET = os.environ["JWT_SECRET"]
    FRONTEND_URL = os.environ["FRONTEND_URL"].rstrip("/")
    ADMIN_EMAIL = os.environ["ADMIN_EMAIL"].lower()
    ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
    ADMIN_EMAIL_DOMAIN = os.environ["ADMIN_EMAIL_DOMAIN"].lower()
    EMERGENT_EMAIL_KEY = os.environ["EMERGENT_EMAIL_KEY"]
    EMAIL_FROM_NAME = os.environ["EMAIL_FROM_NAME"]
    EMAIL_REPLY_TO = os.environ.get("EMAIL_REPLY_TO")
    ENROLLMENT_FEE = 5
    ANNUAL_FEE = 60
    TIMEZONE = "Europe/Rome"
    ACCESS_TOKEN_MINUTES = 60
    REFRESH_TOKEN_DAYS = 7


settings = Settings()
