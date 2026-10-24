# Giguiya API regression tests: health, public events/projects, bookings, member registration,
# auth (login/lockout/admin register/verify/set-password), member dashboard, admin CRUD.
# NOTE: run serially (pytest -n 0): module cleanup fixture deletes TEST_ data and would race under xdist.
import hashlib
import os
import secrets
import subprocess
import uuid
from datetime import datetime

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
API = f"{BASE_URL}/api"
PG = "postgresql://giguiya:giguiya_pg_2026@localhost:5432/giguiya"
ADMIN = {"email": "admin@giguiya.it", "password": "Giguiya@Admin2026"}
RUN = uuid.uuid4().hex[:6]
EVENT_SLUG = "laboratorio-cucina-maliana"


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


@pytest.fixture(scope="module")
def admin():
    s = session()
    r = s.post(f"{API}/auth/login", json=ADMIN)
    if r.status_code != 200:
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
        assert r.status_code == 200
        slugs = [e["slug"] for e in r.json()]
        assert EVENT_SLUG in slugs

    def test_event_detail_and_404(self):
        r = requests.get(f"{API}/events/{EVENT_SLUG}")
        assert r.status_code == 200 and r.json()["slug"] == EVENT_SLUG
        assert requests.get(f"{API}/events/does-not-exist").status_code == 404

    def test_projects_seeded(self):
        slugs = [p["slug"] for p in requests.get(f"{API}/projects").json()]
        for s in ("sport-squadra-maschile", "intrecci-di-comunita", "progetto-baliba"):
            assert s in slugs
        assert requests.get(f"{API}/projects/progetto-baliba").status_code == 200
        assert requests.get(f"{API}/projects/nope-xyz").status_code == 404


# --- bookings ---
class TestBookings:
    def test_booking_validation(self):
        r = requests.post(f"{API}/events/{EVENT_SLUG}/bookings", json={"first_name": "", "last_name": "x", "email": "bad"})
        assert r.status_code == 422

    def test_booking_and_duplicate(self):
        payload = {"first_name": "TEST_Mario", "last_name": "Rossi", "email": f"test_book_{RUN}@example.com"}
        before = requests.get(f"{API}/events/{EVENT_SLUG}").json()["bookings_count"]
        r = requests.post(f"{API}/events/{EVENT_SLUG}/bookings", json=payload)
        assert r.status_code == 201, r.text
        assert "id" in r.json()
        after = requests.get(f"{API}/events/{EVENT_SLUG}").json()["bookings_count"]
        assert after == before + 1
        r2 = requests.post(f"{API}/events/{EVENT_SLUG}/bookings", json={**payload, "email": payload["email"].upper()})
        assert r2.status_code == 409


# --- auth ---
class TestAuth:
    def test_admin_login_cookies(self):
        r = requests.post(f"{API}/auth/login", json=ADMIN)
        assert r.status_code == 200 and r.json()["role"] == "admin"
        sc = r.headers.get("set-cookie", "").lower()
        assert "access_token=" in sc and "httponly" in sc and "secure" in sc and "samesite=none" in sc

    def test_bcrypt_hash(self):
        assert psql("select password_hash from users where email='admin@giguiya.it'").startswith("$2b$")

    def test_cors_credentials(self):
        r = requests.options(f"{API}/auth/login", headers={"Origin": BASE_URL, "Access-Control-Request-Method": "POST"})
        assert r.headers.get("access-control-allow-origin") == BASE_URL
        assert r.headers.get("access-control-allow-credentials") == "true"

    def test_me_unauth(self):
        assert requests.get(f"{API}/auth/me").status_code == 401

    def test_bruteforce_lockout(self):
        email = f"test_brute_{RUN}@example.com"
        codes = [requests.post(f"{API}/auth/login", json={"email": email, "password": "wrong"}).status_code for _ in range(6)]
        assert codes[:5] == [401] * 5, codes
        assert codes[5] == 429, codes

    def test_admin_register_wrong_domain(self):
        r = requests.post(f"{API}/auth/admin/register", json={"first_name": "T", "last_name": "T", "email": f"test_{RUN}@gmail.com", "password": "Password123"})
        assert r.status_code == 400

    def test_admin_register_verify_flow(self):
        email = f"test_adm_{RUN}@giguiya.it"
        r = requests.post(f"{API}/auth/admin/register", json={"first_name": "TEST", "last_name": "Adm", "email": email, "password": "Password123"})
        assert r.status_code == 200, r.text
        assert psql(f"select email_verified from users where email='{email}'") == "f"
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": "Password123"})
        assert r.status_code == 403
        uid = psql(f"select id from users where email='{email}'")
        raw = make_token(uid, "verify_email")
        assert requests.post(f"{API}/auth/verify-email", json={"token": raw}).status_code == 200
        assert requests.post(f"{API}/auth/verify-email", json={"token": raw}).status_code == 400  # reused
        s = session()
        assert s.post(f"{API}/auth/login", json={"email": email, "password": "Password123"}).status_code == 200
        assert s.get(f"{API}/admin/stats").status_code == 200


# --- member flow ---
class TestMember:
    def test_member_full_flow(self, admin):
        email = f"test_member_{RUN}@example.com"
        reg = {"first_name": "TEST_Awa", "last_name": "Traore", "email": email, "privacy_accepted": True}
        r = requests.post(f"{API}/members/register", json=reg)
        assert r.status_code == 201, r.text
        assert requests.post(f"{API}/members/register", json=reg).status_code == 409
        assert requests.post(f"{API}/members/register", json={**reg, "email": f"test_np_{RUN}@example.com", "privacy_accepted": False}).status_code == 422
        # login before password set
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": "whatever1"})
        assert r.status_code == 401
        uid = psql(f"select id from users where email='{email}'")
        raw = make_token(uid)
        assert requests.post(f"{API}/auth/set-password", json={"token": raw, "password": "Member@1234"}).status_code == 200
        # booking with member email
        requests.post(f"{API}/events/{EVENT_SLUG}/bookings", json={"first_name": "TEST_Awa", "last_name": "T", "email": email})
        m = session()
        r = m.post(f"{API}/auth/login", json={"email": email, "password": "Member@1234"})
        assert r.status_code == 200 and r.json()["role"] == "member"
        d = m.get(f"{API}/members/me").json()
        assert d["member"]["in_good_standing"] is False
        assert len(d["bookings"]) == 1
        assert m.get(f"{API}/admin/stats").status_code == 403
        assert m.get(f"{API}/admin/members").status_code == 403
        # admin toggles
        mid = d["member"]["id"]
        year = d["member"]["current_year"]
        r = admin.patch(f"{API}/admin/members/{mid}", json={"enrollment_paid": True, "card_issued": True, "notes": "TEST note"})
        assert r.status_code == 200 and r.json()["enrollment_paid"] and r.json()["card_issued"]
        r = admin.put(f"{API}/admin/members/{mid}/fees/{year}", json={"paid": True})
        assert r.status_code == 200 and r.json()["in_good_standing"] is True
        assert m.get(f"{API}/members/me").json()["member"]["in_good_standing"] is True
        assert admin.put(f"{API}/admin/members/{mid}/fees/1990", json={"paid": True}).status_code == 400
        # contacts include member
        contacts = admin.get(f"{API}/admin/contacts", params={"q": f"test_member_{RUN}"}).json()
        assert contacts and contacts[0]["is_member"] is True
        # change password
        assert m.post(f"{API}/auth/change-password", json={"current_password": "bad", "new_password": "Member@9999"}).status_code == 400
        assert m.post(f"{API}/auth/change-password", json={"current_password": "Member@1234", "new_password": "Member@9999"}).status_code == 200
        # logout
        assert m.post(f"{API}/auth/logout").status_code == 200
        m.cookies.clear()
        assert m.get(f"{API}/members/me").status_code == 401
        # delete
        assert admin.delete(f"{API}/admin/members/{mid}").status_code == 200
        assert admin.get(f"{API}/admin/members/{mid}").status_code == 404


# --- admin CRUD ---
class TestAdminCrud:
    def test_admin_requires_auth(self):
        assert requests.get(f"{API}/admin/stats").status_code == 401

    def test_stats(self, admin):
        d = admin.get(f"{API}/admin/stats").json()
        assert d["projects_total"] >= 3 and d["current_year"] == datetime.now().year

    def test_event_crud(self, admin):
        payload = {"title": f"TEST_Evento {RUN}", "start_at": "2027-03-10T18:00", "end_at": "2027-03-10T20:00", "capacity": 1, "location": "Torino"}
        r = admin.post(f"{API}/admin/events", json=payload)
        assert r.status_code == 201, r.text
        ev = r.json()
        assert requests.get(f"{API}/events/{ev['slug']}").status_code == 200
        # capacity
        assert requests.post(f"{API}/events/{ev['slug']}/bookings", json={"first_name": "TEST_a", "last_name": "b", "email": f"test_c1_{RUN}@example.com"}).status_code == 201
        assert requests.post(f"{API}/events/{ev['slug']}/bookings", json={"first_name": "TEST_a", "last_name": "b", "email": f"test_c2_{RUN}@example.com"}).status_code == 400
        b = admin.get(f"{API}/admin/events/{ev['id']}/bookings").json()
        assert len(b) == 1
        bad = admin.post(f"{API}/admin/events", json={**payload, "end_at": "2027-03-09T10:00"})
        assert bad.status_code == 400
        r = admin.put(f"{API}/admin/events/{ev['id']}", json={**payload, "title": f"TEST_Evento mod {RUN}"})
        assert r.status_code == 200 and r.json()["title"].startswith("TEST_Evento mod")
        assert admin.delete(f"{API}/admin/events/{ev['id']}").status_code == 200
        assert admin.delete(f"{API}/admin/events/{ev['id']}").status_code == 404

    def test_project_crud(self, admin):
        payload = {"title": f"TEST_Progetto {RUN}", "highlights": ["uno", "due"], "summary": "s"}
        r = admin.post(f"{API}/admin/projects", json=payload)
        assert r.status_code == 201, r.text
        p = r.json()
        pub = requests.get(f"{API}/projects/{p['slug']}").json()
        assert pub["highlights"] == ["uno", "due"]
        r = admin.put(f"{API}/admin/projects/{p['id']}", json={**payload, "subtitle": "sub"})
        assert r.status_code == 200 and r.json()["subtitle"] == "sub"
        assert admin.delete(f"{API}/admin/projects/{p['id']}").status_code == 200
        assert requests.get(f"{API}/projects/{p['slug']}").status_code == 404
