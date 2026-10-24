# Giguiya API regression tests: health, public events/projects, bookings, member registration,
# auth (login/lockout/admin register/verify/set-password), member dashboard, admin CRUD.
# NOTE: run serially (pytest -n 0): module cleanup fixture deletes TEST_ data and would race under xdist.
import hashlib
import os
import secrets
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

import pytest
import requests
from dotenv import dotenv_values

BACKEND_ENV = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
FRONTEND_ENV = dotenv_values(Path(__file__).resolve().parents[2] / "frontend" / ".env")

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or FRONTEND_ENV["REACT_APP_BACKEND_URL"]).rstrip("/")
API = f"{BASE_URL}/api"
PG = BACKEND_ENV["DATABASE_URL"].replace("+asyncpg", "")
ADMIN = {"email": BACKEND_ENV["ADMIN_EMAIL"], "password": BACKEND_ENV["ADMIN_PASSWORD"]}
RUN = uuid.uuid4().hex[:6]
EVENT_SLUG = "laboratorio-cucina-maliana"
HTTP_OK, HTTP_CREATED, HTTP_BAD, HTTP_UNAUTH, HTTP_FORBIDDEN = 200, 201, 400, 401, 403
HTTP_NOT_FOUND, HTTP_CONFLICT, HTTP_UNPROCESSABLE, HTTP_TOO_MANY = 404, 409, 422, 429


def random_password() -> str:
    return f"T{secrets.token_urlsafe(12)}9"


def psql(sql: str) -> str:
    return subprocess.run(["psql", PG, "-At", "-c", sql], capture_output=True, text=True, check=True).stdout.strip()


def make_token(user_id: str, purpose: str = "set_password") -> str:
    raw = secrets.token_urlsafe(32)
    h = hashlib.sha256(raw.encode()).hexdigest()
    psql(f"insert into auth_tokens(id, token_hash, user_id, purpose, expires_at, created_at) values "
         f"('{uuid.uuid4()}', '{h}', '{user_id}', '{purpose}', now() + interval '1 day', now())")
    return raw


def session():
    s = requests.Session()
    s.headers.update({"Origin": BASE_URL})
    return s


def book(slug: str, email: str, first_name: str = "TEST_a"):
    return requests.post(f"{API}/events/{slug}/bookings", json={"first_name": first_name, "last_name": "b", "email": email})


@pytest.fixture(scope="module")
def admin():
    s = session()
    r = s.post(f"{API}/auth/login", json=ADMIN)
    if r.status_code != HTTP_OK:
        pytest.skip(f"admin login failed {r.status_code} {r.text}")
    return s


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    psql("delete from bookings where lower(email) like 'test_%' or lower(first_name) like 'test_%'")
    psql("delete from users where lower(email) like 'test_%'")
    psql("delete from login_attempts where identifier like '%test_%'")
    psql("delete from events where title like 'TEST_%'")
    psql("delete from projects where title like 'TEST_%'")


# --- public ---
class TestPublic:
    def test_health(self):
        assert requests.get(f"{API}/health").json() == {"status": "ok"}

    def test_events_list(self):
        r = requests.get(f"{API}/events")
        assert r.status_code == HTTP_OK
        assert EVENT_SLUG in [e["slug"] for e in r.json()]

    def test_event_detail_and_404(self):
        r = requests.get(f"{API}/events/{EVENT_SLUG}")
        assert r.status_code == HTTP_OK and r.json()["slug"] == EVENT_SLUG
        assert requests.get(f"{API}/events/does-not-exist").status_code == HTTP_NOT_FOUND

    def test_projects_seeded(self):
        slugs = [p["slug"] for p in requests.get(f"{API}/projects").json()]
        for s in ("sport-squadra-maschile", "intrecci-di-comunita", "progetto-baliba"):
            assert s in slugs
        assert requests.get(f"{API}/projects/progetto-baliba").status_code == HTTP_OK
        assert requests.get(f"{API}/projects/nope-xyz").status_code == HTTP_NOT_FOUND


# --- bookings ---
class TestBookings:
    def test_booking_validation(self):
        r = requests.post(f"{API}/events/{EVENT_SLUG}/bookings", json={"first_name": "", "last_name": "x", "email": "bad"})
        assert r.status_code == HTTP_UNPROCESSABLE

    def test_booking_and_duplicate(self):
        email = f"test_book_{RUN}@example.com"
        before = requests.get(f"{API}/events/{EVENT_SLUG}").json()["bookings_count"]
        r = book(EVENT_SLUG, email, "TEST_Mario")
        assert r.status_code == HTTP_CREATED, r.text
        assert "id" in r.json()
        assert requests.get(f"{API}/events/{EVENT_SLUG}").json()["bookings_count"] == before + 1
        assert book(EVENT_SLUG, email.upper(), "TEST_Mario").status_code == HTTP_CONFLICT


# --- auth ---
class TestAuth:
    def test_admin_login_cookies(self):
        r = requests.post(f"{API}/auth/login", json=ADMIN)
        assert r.status_code == HTTP_OK and r.json()["role"] == "admin"
        cookie_header = r.headers.get("set-cookie", "").lower()
        for flag in ("access_token=", "httponly", "secure", "samesite=none"):
            assert flag in cookie_header

    def test_bcrypt_hash(self):
        assert psql(f"select password_hash from users where email='{ADMIN['email']}'").startswith("$2b$")

    def test_cors_credentials(self):
        r = requests.options(f"{API}/auth/login", headers={"Origin": BASE_URL, "Access-Control-Request-Method": "POST"})
        assert r.headers.get("access-control-allow-origin") == BASE_URL
        assert r.headers.get("access-control-allow-credentials") == "true"

    def test_me_unauth(self):
        assert requests.get(f"{API}/auth/me").status_code == HTTP_UNAUTH

    def test_bruteforce_lockout(self):
        creds = {"email": f"test_brute_{RUN}@example.com", "password": random_password()}
        codes = [requests.post(f"{API}/auth/login", json=creds).status_code for _ in range(6)]
        assert codes[:5] == [HTTP_UNAUTH] * 5, codes
        assert codes[5] == HTTP_TOO_MANY, codes

    def test_admin_register_wrong_domain(self):
        data = {"first_name": "T", "last_name": "T", "email": f"test_{RUN}@gmail.com", "password": random_password()}
        assert requests.post(f"{API}/auth/admin/register", json=data).status_code == HTTP_BAD

    def test_admin_register_verify_flow(self):
        creds = {"email": f"test_adm_{RUN}@giguiya.it", "password": random_password()}
        r = requests.post(f"{API}/auth/admin/register", json={"first_name": "TEST", "last_name": "Adm", **creds})
        assert r.status_code == HTTP_OK, r.text
        assert psql(f"select email_verified from users where email='{creds['email']}'") == "f"
        assert requests.post(f"{API}/auth/login", json=creds).status_code == HTTP_FORBIDDEN
        raw = make_token(psql(f"select id from users where email='{creds['email']}'"), "verify_email")
        assert requests.post(f"{API}/auth/verify-email", json={"token": raw}).status_code == HTTP_OK
        assert requests.post(f"{API}/auth/verify-email", json={"token": raw}).status_code == HTTP_BAD
        s = session()
        assert s.post(f"{API}/auth/login", json=creds).status_code == HTTP_OK
        assert s.get(f"{API}/admin/stats").status_code == HTTP_OK


# --- member flow ---
@pytest.fixture(scope="module")
def registered_member():
    email = f"test_member_{RUN}@example.com"
    reg = {"first_name": "TEST_Awa", "last_name": "Traore", "email": email, "privacy_accepted": True}
    r = requests.post(f"{API}/members/register", json=reg)
    assert r.status_code == HTTP_CREATED, r.text
    return {"email": email, "reg": reg, "user_id": psql(f"select id from users where email='{email}'")}


@pytest.fixture(scope="module")
def member(registered_member):
    password = random_password()
    raw = make_token(registered_member["user_id"])
    assert requests.post(f"{API}/auth/set-password", json={"token": raw, "password": password}).status_code == HTTP_OK
    s = session()
    r = s.post(f"{API}/auth/login", json={"email": registered_member["email"], "password": password})
    assert r.status_code == HTTP_OK and r.json()["role"] == "member"
    dash = s.get(f"{API}/members/me").json()["member"]
    return {**registered_member, "session": s, "password": password, "id": dash["id"], "year": dash["current_year"]}


class TestMember:
    def test_duplicate_and_privacy(self, registered_member):
        reg = registered_member["reg"]
        assert requests.post(f"{API}/members/register", json=reg).status_code == HTTP_CONFLICT
        bad = {**reg, "email": f"test_np_{RUN}@example.com", "privacy_accepted": False}
        assert requests.post(f"{API}/members/register", json=bad).status_code == HTTP_UNPROCESSABLE

    def test_login_before_password_set(self, registered_member):
        creds = {"email": registered_member["email"], "password": random_password()}
        assert requests.post(f"{API}/auth/login", json=creds).status_code == HTTP_UNAUTH

    def test_dashboard_and_bookings(self, member):
        book(EVENT_SLUG, member["email"], "TEST_Awa")
        d = member["session"].get(f"{API}/members/me").json()
        assert not d["member"]["in_good_standing"]
        assert len(d["bookings"]) == 1

    def test_member_cannot_access_admin(self, member):
        assert member["session"].get(f"{API}/admin/stats").status_code == HTTP_FORBIDDEN
        assert member["session"].get(f"{API}/admin/members").status_code == HTTP_FORBIDDEN

    def test_admin_marks_payments(self, admin, member):
        url = f"{API}/admin/members/{member['id']}"
        r = admin.patch(url, json={"enrollment_paid": True, "card_issued": True, "notes": "TEST note"})
        assert r.status_code == HTTP_OK and r.json()["enrollment_paid"] and r.json()["card_issued"]
        r = admin.put(f"{url}/fees/{member['year']}", json={"paid": True})
        assert r.status_code == HTTP_OK and r.json()["in_good_standing"]
        assert member["session"].get(f"{API}/members/me").json()["member"]["in_good_standing"]
        assert admin.put(f"{url}/fees/1990", json={"paid": True}).status_code == HTTP_BAD

    def test_contacts_flag_member(self, admin, member):
        contacts = admin.get(f"{API}/admin/contacts", params={"q": f"test_member_{RUN}"}).json()
        assert contacts and contacts[0]["is_member"]

    def test_change_password(self, member):
        s = member["session"]
        new = random_password()
        assert s.post(f"{API}/auth/change-password", json={"current_password": "bad", "new_password": new}).status_code == HTTP_BAD
        assert s.post(f"{API}/auth/change-password", json={"current_password": member["password"], "new_password": new}).status_code == HTTP_OK

    def test_logout_and_delete(self, admin, member):
        s = member["session"]
        assert s.post(f"{API}/auth/logout").status_code == HTTP_OK
        s.cookies.clear()
        assert s.get(f"{API}/members/me").status_code == HTTP_UNAUTH
        assert admin.delete(f"{API}/admin/members/{member['id']}").status_code == HTTP_OK
        assert admin.get(f"{API}/admin/members/{member['id']}").status_code == HTTP_NOT_FOUND


# --- admin CRUD ---
EVENT_PAYLOAD = {"title": f"TEST_Evento {RUN}", "start_at": "2027-03-10T18:00", "end_at": "2027-03-10T20:00",
                 "capacity": 1, "location": "Torino"}


@pytest.fixture(scope="class")
def test_event(admin):
    r = admin.post(f"{API}/admin/events", json=EVENT_PAYLOAD)
    assert r.status_code == HTTP_CREATED, r.text
    return r.json()


class TestAdminCrud:
    def test_admin_requires_auth(self):
        assert requests.get(f"{API}/admin/stats").status_code == HTTP_UNAUTH

    def test_stats(self, admin):
        d = admin.get(f"{API}/admin/stats").json()
        assert d["projects_total"] >= 3 and d["current_year"] == datetime.now().year

    def test_event_public_and_capacity(self, admin, test_event):
        assert requests.get(f"{API}/events/{test_event['slug']}").status_code == HTTP_OK
        assert book(test_event["slug"], f"test_c1_{RUN}@example.com").status_code == HTTP_CREATED
        assert book(test_event["slug"], f"test_c2_{RUN}@example.com").status_code == HTTP_BAD
        assert len(admin.get(f"{API}/admin/events/{test_event['id']}/bookings").json()) == 1

    def test_event_invalid_dates(self, admin):
        bad = admin.post(f"{API}/admin/events", json={**EVENT_PAYLOAD, "end_at": "2027-03-09T10:00"})
        assert bad.status_code == HTTP_BAD

    def test_event_update_and_delete(self, admin, test_event):
        url = f"{API}/admin/events/{test_event['id']}"
        r = admin.put(url, json={**EVENT_PAYLOAD, "title": f"TEST_Evento mod {RUN}"})
        assert r.status_code == HTTP_OK and r.json()["title"].startswith("TEST_Evento mod")
        assert admin.delete(url).status_code == HTTP_OK
        assert admin.delete(url).status_code == HTTP_NOT_FOUND

    def test_project_crud(self, admin):
        payload = {"title": f"TEST_Progetto {RUN}", "highlights": ["uno", "due"], "summary": "s"}
        r = admin.post(f"{API}/admin/projects", json=payload)
        assert r.status_code == HTTP_CREATED, r.text
        p = r.json()
        assert requests.get(f"{API}/projects/{p['slug']}").json()["highlights"] == ["uno", "due"]
        r = admin.put(f"{API}/admin/projects/{p['id']}", json={**payload, "subtitle": "sub"})
        assert r.status_code == HTTP_OK and r.json()["subtitle"] == "sub"
        assert admin.delete(f"{API}/admin/projects/{p['id']}").status_code == HTTP_OK
        assert requests.get(f"{API}/projects/{p['slug']}").status_code == HTTP_NOT_FOUND
