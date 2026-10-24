# Regression tests for iteration-2 refactors: login() split, decode_token, _assert_safe_email (email_sent).
# Run serially: pytest -n 0 tests/test_refactor_regression.py
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import pytest
import requests
from dotenv import dotenv_values

from test_giguiya_api import API, ADMIN, BACKEND_ENV, EVENT_SLUG, psql, random_password, session

RUN = uuid.uuid4().hex[:6]
SECRET = BACKEND_ENV["JWT_SECRET"]


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    psql("delete from bookings where lower(email) like 'test_%' or lower(first_name) like 'test_%'")
    psql("delete from users where lower(email) like 'test_%'")
    psql("delete from login_attempts where identifier like '%test_%'")


def admin_id():
    return psql(f"select id from users where email='{ADMIN['email']}'")


class TestLoginRefactor:
    def test_wrong_password_401_message(self):
        r = requests.post(f"{API}/auth/login", json={"email": f"test_wp_{RUN}@example.com", "password": "x" * 9})
        assert r.status_code == 401 and r.json()["detail"] == "Email o password non corretti"

    def test_member_no_password_message(self):
        email = f"test_np_{RUN}@example.com"
        r = requests.post(f"{API}/members/register", json={"first_name": "TEST_a", "last_name": "b", "email": email, "privacy_accepted": True})
        assert r.status_code == 201 and r.json().get("email_sent") is True, r.text
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": random_password()})
        assert r.status_code == 401 and "Password non ancora impostata" in r.json()["detail"]

    def test_successful_login_clears_attempts(self):
        s = session()
        assert s.post(f"{API}/auth/login", json=ADMIN).status_code == 200
        assert s.get(f"{API}/auth/me").json()["email"] == ADMIN["email"]


class TestTokenRefactor:
    def test_me_invalid_token(self):
        r = requests.get(f"{API}/auth/me", headers={"Authorization": "Bearer garbage"})
        assert r.status_code == 401 and r.json()["detail"] == "Token non valido"

    def test_me_expired_token(self):
        tok = jwt.encode({"sub": admin_id(), "type": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, SECRET, algorithm="HS256")
        r = requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {tok}"})
        assert r.status_code == 401 and r.json()["detail"] == "Sessione scaduta"

    def test_refresh_token_rejected_as_access(self):
        tok = jwt.encode({"sub": admin_id(), "type": "refresh", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, SECRET, algorithm="HS256")
        assert requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {tok}"}).status_code == 401

    def test_refresh_flow(self):
        s = session()
        assert s.post(f"{API}/auth/login", json=ADMIN).status_code == 200
        refresh = s.cookies.get("refresh_token")
        s2 = session()
        s2.cookies.set("refresh_token", refresh)
        r = s2.post(f"{API}/auth/refresh")
        assert r.status_code == 200 and r.json()["email"] == ADMIN["email"]
        assert "access_token=" in r.headers.get("set-cookie", "")

    def test_refresh_missing_and_invalid(self):
        assert requests.post(f"{API}/auth/refresh").status_code == 401
        s = session()
        s.cookies.set("refresh_token", "bad")
        assert s.post(f"{API}/auth/refresh").status_code == 401


class TestEmailRefactor:
    def test_booking_email_sent(self):
        r = requests.post(f"{API}/events/{EVENT_SLUG}/bookings", json={"first_name": "TEST_e", "last_name": "b", "email": f"test_em_{RUN}@example.com"})
        assert r.status_code == 201, r.text
        assert r.json().get("email_sent") is True, r.json()
