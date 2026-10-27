"""Giguiya API regression on MongoDB: public, booking, members, auth, admin, file storage."""
import io
import uuid
from datetime import datetime

import pytest
import requests

from conftest import API, ADMIN_DOMAIN, ADMIN_EMAIL, ADMIN_PASSWORD, DB, future_local, insert_token, make_email

SEED_PROJECTS = {"sport-squadra-maschile", "intrecci-di-comunita", "progetto-baliba"}
SEED_EVENTS = {"laboratorio-treccine-maliane", "laboratorio-cucina-maliana", "serata-musicale-maliana"}
YEAR = datetime.now().year


def register_member(tag="m", **extra):
    email = extra.pop("email", None) or make_email(tag)
    payload = {"first_name": "Test", "last_name": "Socio", "email": email, "phone": "+39 333", "city": "Roma",
               "privacy_accepted": True, **extra}
    return email, requests.post(f"{API}/members/register", json=payload)


def member_session(email):
    user = DB.users.find_one({"email": email})
    raw = insert_token(user["id"], "set_password")
    r = requests.post(f"{API}/auth/set-password", json={"token": raw, "password": "TestPass123!"})
    assert r.status_code == 200, r.text
    s = requests.Session()
    assert s.post(f"{API}/auth/login", json={"email": email, "password": "TestPass123!"}).status_code == 200
    return s, user


def png_bytes():
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (200, 30, 30)).save(buf, "PNG")
    return buf.getvalue()


# ---------- Public events/projects ----------
class TestPublic:
    def test_health(self):
        assert requests.get(f"{API}/health").json() == {"status": "ok"}

    def test_events_scopes(self):
        allev = requests.get(f"{API}/events", params={"scope": "all"}).json()
        assert SEED_EVENTS <= {e["slug"] for e in allev}
        up = requests.get(f"{API}/events").json()
        assert all(not e["is_past"] for e in up)
        past = requests.get(f"{API}/events", params={"scope": "past"})
        assert past.status_code == 200 and all(e["is_past"] for e in past.json())
        assert requests.get(f"{API}/events", params={"scope": "bogus"}).status_code == 422

    def test_event_detail(self):
        r = requests.get(f"{API}/events/laboratorio-cucina-maliana")
        assert r.status_code == 200 and r.json()["slug"] == "laboratorio-cucina-maliana"
        assert "_id" not in r.json()
        assert requests.get(f"{API}/events/does-not-exist").status_code == 404

    def test_projects(self):
        r = requests.get(f"{API}/projects")
        assert r.status_code == 200 and SEED_PROJECTS <= {p["slug"] for p in r.json()}
        d = requests.get(f"{API}/projects/progetto-baliba")
        assert d.status_code == 200 and d.json()["title"] == "Progetto Baliba"
        assert requests.get(f"{API}/projects/nope-xyz").status_code == 404


# ---------- Bookings ----------
class TestBookings:
    def test_booking_flow(self, admin_client):
        ev = admin_client.post(f"{API}/admin/events", json={"title": f"TEST_Cap {uuid.uuid4().hex[:6]}",
                                                             "start_at": future_local(), "capacity": 2}).json()
        e1 = "delivered@resend.dev"
        r = requests.post(f"{API}/events/{ev['slug']}/bookings", json={"first_name": "T", "last_name": "B", "email": e1})
        assert r.status_code == 201, r.text
        assert r.json()["email_sent"] in (True, False) and r.json()["id"]
        dup = requests.post(f"{API}/events/{ev['slug']}/bookings", json={"first_name": "T", "last_name": "B", "email": e1})
        assert dup.status_code == 409
        assert requests.post(f"{API}/events/{ev['slug']}/bookings",
                             json={"first_name": "T", "last_name": "B", "email": make_email("fill")}).status_code == 201
        full = requests.post(f"{API}/events/{ev['slug']}/bookings",
                             json={"first_name": "T", "last_name": "B", "email": make_email("full")})
        assert full.status_code == 400 and "completo" in full.json()["detail"]
        bad = requests.post(f"{API}/events/{ev['slug']}/bookings", json={"first_name": "", "last_name": "B", "email": "x"})
        assert bad.status_code == 422
        bl = admin_client.get(f"{API}/admin/events/{ev['id']}/bookings").json()
        assert len(bl) == 2 and e1 in {b["email"] for b in bl}
        assert admin_client.delete(f"{API}/admin/bookings/{bl[0]['id']}").status_code == 200
        assert admin_client.delete(f"{API}/admin/bookings/{bl[0]['id']}").status_code == 404
        assert admin_client.delete(f"{API}/admin/events/{ev['id']}").status_code == 200

    def test_seed_event_booking_email_sent(self):
        r = requests.post(f"{API}/events/laboratorio-cucina-maliana/bookings",
                          json={"first_name": "Test", "last_name": "Seed", "email": make_email("seedbk")})
        assert r.status_code == 201 and isinstance(r.json()["email_sent"], bool)


# ---------- Member registration + dashboard ----------
class TestMembers:
    def test_register_and_numbers(self):
        e1, r1 = register_member("reg1")
        assert r1.status_code == 201, r1.text
        e2, r2 = register_member("reg2")
        assert r2.status_code == 201
        n1 = DB.users.find_one({"email": e1})["member"]["membership_number"]
        n2 = DB.users.find_one({"email": e2})["member"]["membership_number"]
        assert n1.startswith(f"GIG-{YEAR}-") and int(n2[-4:]) == int(n1[-4:]) + 1
        _, dup = register_member(email=e1)
        assert dup.status_code == 409
        _, nop = register_member("nopriv", privacy_accepted=False)
        assert nop.status_code == 422

    def test_member_dashboard_and_blocked(self):
        email, r = register_member("dash")
        assert r.status_code == 201
        requests.post(f"{API}/events/serata-musicale-maliana/bookings",
                      json={"first_name": "T", "last_name": "S", "email": email})
        s, _ = member_session(email)
        me = s.get(f"{API}/members/me")
        assert me.status_code == 200
        body = me.json()
        assert body["member"]["in_good_standing"] is False and body["member"]["account_active"] is True
        assert any(b["event_slug"] == "serata-musicale-maliana" for b in body["bookings"])
        assert s.get(f"{API}/admin/stats").status_code == 403
        up = s.post(f"{API}/admin/uploads", files={"file": ("test_m.png", png_bytes(), "image/png")})
        assert up.status_code == 403


# ---------- Auth ----------
class TestAuth:
    def test_admin_login_cookies_me_refresh_logout(self):
        s = requests.Session()
        r = s.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert r.status_code == 200 and r.json()["role"] == "admin" and "password_hash" not in r.json()
        sc = r.headers.get("set-cookie", "").lower()
        assert "access_token" in sc and "refresh_token" in sc and "httponly" in sc
        assert s.get(f"{API}/auth/me").json()["email"] == ADMIN_EMAIL
        assert s.post(f"{API}/auth/refresh").status_code == 200
        assert s.post(f"{API}/auth/logout").status_code == 200
        assert s.get(f"{API}/auth/me").status_code == 401

    def test_bcrypt_hash(self):
        assert DB.users.find_one({"email": ADMIN_EMAIL})["password_hash"].startswith("$2b$")

    def test_wrong_password_and_lockout(self):
        email, _ = register_member("lock")
        s, _ = member_session(email)
        ip = f"10.9.{uuid.uuid4().int % 250}.{uuid.uuid4().int % 250}"
        h = {"X-Forwarded-For": ip}
        codes = [requests.post(f"{API}/auth/login", json={"email": email, "password": "wrong"}, headers=h).status_code
                 for _ in range(5)]
        assert codes == [401] * 5
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": "TestPass123!"}, headers=h)
        assert r.status_code == 429, f"lockout not applied (identifier ip:{ip}) got {r.status_code}"

    def test_member_without_password(self):
        email, _ = register_member("nopw")
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": "whatever1"})
        assert r.status_code == 401 and "Password non ancora impostata" in r.json()["detail"]

    def test_admin_register_flow(self):
        bad = requests.post(f"{API}/auth/admin/register", json={"first_name": "T", "last_name": "A",
                                                                "email": make_email("adm"), "password": "TestPass123!"})
        assert bad.status_code == 400
        email = f"test_adm_{uuid.uuid4().hex[:6]}@{ADMIN_DOMAIN}"
        r = requests.post(f"{API}/auth/admin/register", json={"first_name": "T", "last_name": "A", "email": email,
                                                              "password": "TestPass123!"})
        assert r.status_code == 200, r.text
        assert requests.post(f"{API}/auth/login", json={"email": email, "password": "TestPass123!"}).status_code == 403
        user = DB.users.find_one({"email": email})
        raw = insert_token(user["id"], "verify_email")
        assert requests.post(f"{API}/auth/verify-email", json={"token": raw}).status_code == 200
        assert requests.post(f"{API}/auth/verify-email", json={"token": raw}).status_code == 400
        # since staff-approval feature: verified staff stays pending until super admin approves
        assert requests.post(f"{API}/auth/login", json={"email": email, "password": "TestPass123!"}).status_code == 403

    def test_change_and_forgot_password(self):
        email, _ = register_member("chg")
        s, _ = member_session(email)
        assert s.post(f"{API}/auth/change-password", json={"current_password": "bad", "new_password": "NewPass123!"}).status_code == 400
        assert s.post(f"{API}/auth/change-password", json={"current_password": "TestPass123!", "new_password": "NewPass123!"}).status_code == 200
        assert requests.post(f"{API}/auth/login", json={"email": email, "password": "NewPass123!"}).status_code == 200
        a = requests.post(f"{API}/auth/forgot-password", json={"email": email}).json()["message"]
        b = requests.post(f"{API}/auth/forgot-password", json={"email": make_email("ghost")}).json()["message"]
        assert a == b

    def test_set_password_invalid_token(self):
        assert requests.post(f"{API}/auth/set-password", json={"token": "x" * 40, "password": "TestPass123!"}).status_code == 400


# ---------- Admin ----------
class TestAdmin:
    def test_anon_blocked(self):
        assert requests.get(f"{API}/admin/stats").status_code == 401

    def test_stats(self, admin_client):
        r = admin_client.get(f"{API}/admin/stats")
        assert r.status_code == 200 and r.json()["projects_total"] >= 3 and r.json()["current_year"] == YEAR

    def test_member_management(self, admin_client):
        email, _ = register_member("adm_mgmt")
        mid = DB.users.find_one({"email": email})["id"]
        lst = admin_client.get(f"{API}/admin/members", params={"q": email}).json()
        assert len(lst) == 1 and lst[0]["id"] == mid
        assert any(m["id"] == mid for m in admin_client.get(f"{API}/admin/members", params={"status": "non_in_regola"}).json())
        p = admin_client.patch(f"{API}/admin/members/{mid}", json={"enrollment_paid": True, "card_issued": True, "notes": "TEST note"}).json()
        assert p["enrollment_paid"] and p["card_issued"] and p["notes"] == "TEST note" and p["enrollment_paid_at"]
        f = admin_client.put(f"{API}/admin/members/{mid}/fees/{YEAR}", json={"paid": True}).json()
        assert f["current_year_paid"] and f["in_good_standing"] and len(f["fees"]) == 1
        f2 = admin_client.put(f"{API}/admin/members/{mid}/fees/{YEAR}", json={"paid": True}).json()
        assert len(f2["fees"]) == 1
        assert any(m["id"] == mid for m in admin_client.get(f"{API}/admin/members", params={"status": "in_regola"}).json())
        f3 = admin_client.put(f"{API}/admin/members/{mid}/fees/{YEAR}", json={"paid": False}).json()
        assert not f3["in_good_standing"] and f3["fees"] == []
        assert admin_client.put(f"{API}/admin/members/{mid}/fees/1990", json={"paid": True}).status_code == 400
        ri = admin_client.post(f"{API}/admin/members/{mid}/resend-invite")
        assert ri.status_code == 200 and "email_sent" in ri.json()
        assert admin_client.delete(f"{API}/admin/members/{mid}").status_code == 200
        assert admin_client.get(f"{API}/admin/members/{mid}").status_code == 404
        assert DB.auth_tokens.count_documents({"user_id": mid}) == 0

    def test_contacts(self, admin_client):
        email, _ = register_member("contact")
        requests.post(f"{API}/events/laboratorio-treccine-maliane/bookings", json={"first_name": "T", "last_name": "C", "email": email})
        rows = admin_client.get(f"{API}/admin/contacts", params={"q": email}).json()
        assert len(rows) == 1 and rows[0]["is_member"] is True and rows[0]["bookings_count"] == 1

    def test_events_crud_timezone(self, admin_client):
        title = f"TEST_Evento {uuid.uuid4().hex[:6]}"
        start = future_local(20, 18)
        r = admin_client.post(f"{API}/admin/events", json={"title": title, "start_at": start, "location": "Roma",
                                                            "image_url": "/api/files/giguiya/images/x.png"})
        assert r.status_code == 201, r.text
        ev = r.json()
        assert ev["start_local"] == start
        stored = DB.events.find_one({"id": ev["id"]})["start_at"]
        assert stored.utcoffset().total_seconds() == 0 and stored.hour in (16, 17)  # Europe/Rome -> UTC
        bad = admin_client.post(f"{API}/admin/events", json={"title": title, "start_at": start, "end_at": future_local(19)})
        assert bad.status_code == 400
        u = admin_client.put(f"{API}/admin/events/{ev['id']}", json={"title": title + " upd", "start_at": start, "capacity": 5})
        assert u.status_code == 200 and u.json()["capacity"] == 5 and u.json()["spots_left"] == 5
        assert requests.get(f"{API}/events/{u.json()['slug']}").json()["title"] == title + " upd"
        assert admin_client.delete(f"{API}/admin/events/{ev['id']}").status_code == 200
        assert admin_client.delete(f"{API}/admin/events/{ev['id']}").status_code == 404

    def test_projects_crud(self, admin_client):
        title = f"TEST_Progetto {uuid.uuid4().hex[:6]}"
        r = admin_client.post(f"{API}/admin/projects", json={"title": title, "highlights": ["a", "b"]})
        assert r.status_code == 201
        p = r.json()
        assert p["highlights"] == ["a", "b"] and p["slug"]
        assert requests.get(f"{API}/projects/{p['slug']}").json()["highlights"] == ["a", "b"]
        u = admin_client.put(f"{API}/admin/projects/{p['id']}", json={"title": title, "highlights": ["c"], "is_published": False})
        assert u.json()["highlights"] == ["c"]
        assert requests.get(f"{API}/projects/{p['slug']}").status_code == 404
        assert admin_client.delete(f"{API}/admin/projects/{p['id']}").status_code == 200
        assert admin_client.get(f"{API}/admin/projects").status_code == 200


# ---------- File storage ----------
class TestUploads:
    def test_anon_upload_401(self):
        r = requests.post(f"{API}/admin/uploads", files={"file": ("test_a.png", png_bytes(), "image/png")})
        assert r.status_code == 401

    def test_upload_and_serve(self, admin_client):
        data = png_bytes()
        r = admin_client.post(f"{API}/admin/uploads", files={"file": ("test_up.png", data, "image/png")})
        assert r.status_code in (200, 201), r.text
        url = r.json()["url"]
        assert url.startswith("/api/files/giguiya/images/") and url.endswith(".png")
        g = requests.get(API.rsplit("/api", 1)[0] + url)
        assert g.status_code == 200 and g.headers["content-type"].startswith("image/png") and g.content == data

    def test_reject_type_and_size(self, admin_client):
        t = admin_client.post(f"{API}/admin/uploads", files={"file": ("test_x.txt", b"hello", "text/plain")})
        assert t.status_code == 400
        big = admin_client.post(f"{API}/admin/uploads", files={"file": ("test_big.jpg", b"\xff" * (8 * 1024 * 1024 + 10), "image/jpeg")})
        assert big.status_code == 400

    def test_unknown_file_404(self):
        assert requests.get(f"{API}/files/giguiya/images/{uuid.uuid4()}.png").status_code == 404
