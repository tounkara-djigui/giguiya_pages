import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    MONGO_URL = os.environ["MONGO_URL"]
    DB_NAME = os.environ["DB_NAME"]
    JWT_SECRET = os.environ["JWT_SECRET"]
    FRONTEND_URL = os.environ["FRONTEND_URL"].rstrip("/")
    ADMIN_EMAIL = os.environ["ADMIN_EMAIL"].lower()
    ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
    ADMIN_EMAIL_DOMAIN = os.environ["ADMIN_EMAIL_DOMAIN"].lower()
    EMERGENT_EMAIL_KEY = os.environ.get("EMERGENT_EMAIL_KEY")
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT") or 465)
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    SMTP_FROM = os.environ.get("SMTP_FROM") or os.environ.get("SMTP_USER")
    EMAIL_FROM_NAME = os.environ["EMAIL_FROM_NAME"]
    EMAIL_REPLY_TO = os.environ.get("EMAIL_REPLY_TO")
    ENROLLMENT_FEE = 5
    ANNUAL_FEE = 60
    ENROLLMENT_FEE_LABEL = "xx"
    ANNUAL_FEE_LABEL = "xx"
    TIMEZONE = "Europe/Rome"
    ACCESS_TOKEN_MINUTES = 60
    REFRESH_TOKEN_DAYS = 7


settings = Settings()
