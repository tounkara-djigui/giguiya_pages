# Auth testing notes (Giguiya)

- Login: POST /api/auth/login {email,password} → sets httpOnly cookies access_token/refresh_token; returns user with `role` ("admin" | "member" | "pending") and `is_super_admin`.
- Super admin = backend ADMIN_EMAIL (preview: admin@giguiya.it, see /app/memory/test_credentials.md).
- Staff flow: POST /api/auth/admin/register (email @giguiya.it) → admin_status "pending" → POST /api/auth/verify-email {token} → super admin notified → super admin POST /api/admin/staff/{id}/approve → staff can log in.
- Pending/unapproved staff: login returns 403; all /api/admin/* return 403.
- Super-admin only: GET /api/admin/staff, POST /api/admin/staff/{id}/approve|revoke, DELETE /api/admin/staff/{id}. Approved non-super admins get 403 there.
- Verify-email tokens are stored hashed in `auth_tokens`; for tests create one via app.services.token_service.issue_token(user_id, "verify_email", hours=48) or read DB directly.
