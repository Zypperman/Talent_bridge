# Auth & Accounts

All auth logic lives in [services/auth_service/service.py](../services/auth_service/service.py),
called from the gateway only via RPC (`auth_client.call(...)` in
[gateway/main.py](../gateway/main.py)) — the gateway never touches `users` /
`employers` / `admins` / `auth_tokens` directly, only `auth-service` does.

## Three account types, three tables

There is no shared `accounts` table. `users` (learners), `employers`, and `admins`
are independent tables with independent `id` sequences and independent
signup/login handlers. What ties them together is `auth_tokens.account_type`
(`'user' | 'employer' | 'admin'`) — every gateway route that requires a specific kind
of caller checks `account["account_type"] == "..."` after resolving the token, e.g.:

```python
account = await get_account(authorization)
if account is None or account["account_type"] != "user":
    return {"error": "Not authenticated"}
```

This means a valid employer token hitting a learner-only route (or vice versa) is
treated identically to *no token at all* — you'll get the same `{"error": "Not
authenticated"}`.

## Passwords & tokens

- Passwords are hashed with `bcrypt` (`hash_password`/`verify_password` in
  [service.py](../services/auth_service/service.py)) — never stored or logged in
  plaintext.
- A successful signup or login calls `_create_token(db, account_type, account_id)`,
  which generates a 32-byte URL-safe random token (`secrets.token_urlsafe(32)`) and
  inserts a row into `auth_tokens`. **Tokens never expire** — there's no `expires_at`
  check and no server-side revoke/logout endpoint. Client-side "logout" just deletes
  the token from `localStorage`; the row still exists in `auth_tokens` and would still
  authenticate if replayed.
- Resolving a token happens on nearly every request via `get_account_from_token`,
  which is a single indexed lookup (`auth_tokens.token` is the primary key) followed
  by a lookup into the relevant account table.

## Account shapes

What `GET /api/auth/me` / `get_account_from_token` returns, by type:

```jsonc
// user
{ "account_type": "user", "id", "email", "name", "education", "experience", "current_company", "certifications" }

// employer
{ "account_type": "employer", "id", "email", "company_name", "contact_name" }

// admin
{ "account_type": "admin", "id", "email", "name" }
```

`password_hash` is never included in any of these — the `SELECT` statements in
`get_account_from_token` explicitly list columns rather than `SELECT *`.

## Why admin signup is out-of-band

There is deliberately no `POST /api/auth/signup/admin` route. The admin console
(`static/admin.html`) exposes every learner's private conversation transcripts and
lets an admin fabricate completion scores, so admin accounts are provisioned directly
against the database with [create_admin.py](../create_admin.py) rather than through a
public API:

```bash
docker compose run --rm auth-service python create_admin.py you@example.com yourpassword "Your Name"
```

The script applies `schema.sql` itself (safe/idempotent) so it can be run standalone
before the rest of the stack has ever started, refuses to create a duplicate email,
and hashes the password the same way `auth-service` does.

## Gateway-side auth helper

Every protected route goes through `get_account(authorization)` in
[gateway/main.py](../gateway/main.py):

```python
async def get_account(authorization: str | None):
    if authorization is None:
        return None
    token = authorization.replace("Bearer ", "").strip()
    try:
        return await auth_client.call("get_account_from_token", {"token": token})
    except (ServiceError, ServiceUnavailableError):
        return None
```

Note it swallows *both* a business-logic error and an unreachable auth-service the
same way — as far as a caller can tell, "invalid token" and "auth-service is down"
look identical (`{"error": "Not authenticated"}`). If you're debugging an
unexpected auth failure, check whether `auth-service` is actually up before assuming
the token itself is bad.
