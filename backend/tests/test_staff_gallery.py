"""Staff approval (super admin only) + project gallery tests."""
import uuid

import pytest
import requests

from conftest import API, ADMIN_DOMAIN, ADMIN_EMAIL, ADMIN_PASSWORD, DB, insert_token

PW = "TestPass123!"
REAL_STAFF = "info@giguiya.it"


def login(email, pw=PW):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": pw})
    return s, r


def register_staff():
    email = f"TEST_staff_{uuid.uuid4().hex[:6]}@{ADMIN_DOMAIN}"
    r = requests.post(f"{API}/auth/admin/register", json={"first_name": "Tst", "last_name": "Staff",
                                                          "email": email, "password": PW})
    assert r.status_code == 200, r.text
    return email.lower(), DB.users.find_one({"email": email.lower()})


# ---------- Super admin ----------
class TestSuperAdmin:
    def test_super_admin_login(self):
        s, r = login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert r.status_code == 200
        assert r.json()["role"] == "admin" and r.json()["is_super_admin"] is True
        me = s.get(f"{API}/auth/me").json()
        assert me["is_super_admin"] is True

    def test_real_staff_untouched_and_pending(self, admin_client):
        lst = admin_client.get(f"{API}/admin/staff").json()
        real = [x for x in lst if x["email"] == REAL_STAFF]
        assert ADMIN_EMAIL not in {x["email"] for x in lst}
        if real:
            assert real[0]["admin_status"] == "pending"
        assert all("password_hash" not in x and "_id" not in x for x in lst)


# ---------- Staff lifecycle ----------
class TestStaffFlow:
    def test_full_lifecycle(self, admin_client):
        email, user = register_staff()
        assert user["role"] == "admin" and user["admin_status"] == "pending" and not user["email_verified"]
        _, r = login(email)
        assert r.status_code == 403 and "Conferma" in r.json()["detail"]

        # approve unverified -> 400
        a = admin_client.post(f"{API}/admin/staff/{user['id']}/approve")
        assert a.status_code == 400, a.text

        raw = insert_token(user["id"], "verify_email")
        v = requests.post(f"{API}/auth/verify-email", json={"token": raw})
        assert v.status_code == 200 and "approvazione" in v.json()["message"]
        _, r = login(email)
        assert r.status_code == 403 and "in attesa di approvazione" in r.json()["detail"]

        lst = admin_client.get(f"{API}/admin/staff").json()
        row = next(x for x in lst if x["email"] == email)
        assert row["admin_status"] == "pending" and row["email_verified"] is True

        a = admin_client.post(f"{API}/admin/staff/{user['id']}/approve")
        assert a.status_code == 200 and "email_sent" in a.json()
        s, r = login(email)
        assert r.status_code == 200 and r.json()["role"] == "admin" and r.json()["is_super_admin"] is False
        assert s.get(f"{API}/admin/stats").status_code == 200
        assert s.get(f"{API}/admin/staff").status_code == 403
        assert s.post(f"{API}/admin/staff/{user['id']}/revoke").status_code == 403

        rv = admin_client.post(f"{API}/admin/staff/{user['id']}/revoke")
        assert rv.status_code == 200
        assert DB.users.find_one({"email": email})["admin_status"] == "pending"
        # existing session must lose admin access
        assert s.get(f"{API}/admin/stats").status_code == 403
        assert s.get(f"{API}/auth/me").json()["role"] == "pending"
        _, r = login(email)
        assert r.status_code == 403

        d = admin_client.delete(f"{API}/admin/staff/{user['id']}")
        assert d.status_code == 200
        assert DB.users.find_one({"email": email}) is None
        assert DB.auth_tokens.count_documents({"user_id": user["id"]}) == 0
        assert admin_client.delete(f"{API}/admin/staff/{user['id']}").status_code == 404

    def test_cannot_act_on_super_admin_or_members(self, admin_client):
        sa = DB.users.find_one({"email": ADMIN_EMAIL})
        assert admin_client.post(f"{API}/admin/staff/{sa['id']}/revoke").status_code == 404
        assert admin_client.delete(f"{API}/admin/staff/{sa['id']}").status_code == 404

    def test_anon_staff_401(self):
        assert requests.get(f"{API}/admin/staff").status_code == 401

    def test_reregister_after_verified_409(self, admin_client):
        email, user = register_staff()
        DB.users.update_one({"id": user["id"]}, {"$set": {"email_verified": True}})
        r = requests.post(f"{API}/auth/admin/register", json={"first_name": "X", "last_name": "Y", "email": email,
                                                              "password": PW})
        assert r.status_code == 409
        assert admin_client.delete(f"{API}/admin/staff/{user['id']}").status_code == 200


# ---------- Project gallery ----------
class TestGallery:
    def test_gallery_crud(self, admin_client):
        title = f"TEST_Gallery {uuid.uuid4().hex[:6]}"
        g = [f"/api/files/giguiya/images/t{i}.png" for i in range(3)]
        r = admin_client.post(f"{API}/admin/projects", json={"title": title, "gallery": g})
        assert r.status_code == 201, r.text
        p = r.json()
        assert p["gallery"] == g
        assert requests.get(f"{API}/projects/{p['slug']}").json()["gallery"] == g
        u = admin_client.put(f"{API}/admin/projects/{p['id']}", json={"title": title, "gallery": g[:1]})
        assert u.status_code == 200 and u.json()["gallery"] == g[:1]
        assert requests.get(f"{API}/projects/{p['slug']}").json()["gallery"] == g[:1]
        ok12 = admin_client.put(f"{API}/admin/projects/{p['id']}", json={"title": title, "gallery": g * 4})
        assert ok12.status_code == 200 and len(ok12.json()["gallery"]) == 12
        bad = admin_client.put(f"{API}/admin/projects/{p['id']}", json={"title": title, "gallery": g * 4 + ["x"]})
        assert bad.status_code == 422
        bad2 = admin_client.post(f"{API}/admin/projects", json={"title": title + "b", "gallery": ["x"] * 13})
        assert bad2.status_code == 422
        assert admin_client.delete(f"{API}/admin/projects/{p['id']}").status_code == 200

    def test_old_projects_gallery_list(self):
        for slug in ("giguiya-eventi", "progetto-baliba"):
            r = requests.get(f"{API}/projects/{slug}")
            if r.status_code == 404:
                continue
            assert isinstance(r.json()["gallery"], list)
        for p in requests.get(f"{API}/projects").json():
            assert isinstance(p.get("gallery"), list)
