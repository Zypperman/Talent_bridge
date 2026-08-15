# API Reference

All routes are defined in [gateway/main.py](../gateway/main.py) and mounted under
`/api/*`; everything else (`/`, `/admin.html`, ...) is the static frontend. There is no
`/docs` route disabled — FastAPI's automatic Swagger UI is available at `/docs` and
`/openapi.json` if you want an interactive view of the same routes.

## Conventions

- **Auth header**: `Authorization: Bearer <token>` where `<token>` came from a
  login/signup response. Optional on public routes, required on the rest.
- **Error shape**: every failure — auth, validation, not-found, or a downstream service
  being unavailable — returns HTTP 200 with `{"error": "<message>"}` in the body,
  *not* a 4xx/5xx status. Routes were not written to raise `HTTPException`; check the
  `error` key in the JSON body, not the status code.
- **No pagination** anywhere. `GET /api/admin/users`, `GET /api/employer/candidates`,
  etc. return every row.
- Request bodies are validated by Pydantic models (see the class definitions at the
  top of [gateway/main.py](../gateway/main.py)); a genuinely malformed body (wrong
  types, missing required fields) *will* get FastAPI's standard 422 response, unlike
  business-logic errors.

## Auth

### `POST /api/auth/signup/user`
Create a learner account. Body:
```json
{ "email": "", "password": "", "name": "", "education": "", "experience": "", "current_company": "", "certifications": "" }
```
Only `email`, `password`, `name` are required; the rest default to `""`. Returns
`{"account_id", "account_type": "user", "token"}` or `{"error": "An account with this
email already exists"}`.

### `POST /api/auth/login/user`
Body: `{"email", "password"}`. Returns the same shape as signup, or
`{"error": "Invalid email or password"}`.

### `POST /api/auth/signup/employer` / `POST /api/auth/login/employer`
Same pattern as above. Signup body: `{"email", "password", "company_name",
"contact_name"}` (all required). Returns `{"account_id", "account_type": "employer",
"token"}`.

### `POST /api/auth/login/admin`
Body: `{"email", "password"}`. Returns `{"account_id", "account_type": "admin",
"token"}`. **There is no `signup/admin` route** — admin accounts are created
out-of-band with [create_admin.py](../create_admin.py); see
[auth-and-accounts.md](auth-and-accounts.md).

### `GET /api/auth/me`
Requires auth. Returns `{"account": {...}}` where the shape of `account` depends on
`account_type` (`user` / `employer` / `admin` — see
[auth-and-accounts.md](auth-and-accounts.md#account-shapes)), or `{"error": "Not
authenticated"}` if the token is missing/invalid.

## Courses & sections (learner-facing)

### `GET /api/courses`
Public, no auth required. Returns `{"courses": [{"id", "slug", "title",
"description"}, ...]}` ordered by `display_order`.

### `GET /api/courses/{course_id}/sections`
Auth optional. Returns `{"sections": [{"id", "section_number", "title", "status"},
...]}`. `status` is `"not_started"` when unauthenticated or not a learner account;
otherwise it's per-user, computed from `section_progress` (see
[data-model.md](data-model.md#derived-state)).

### `GET /api/sections/{section_id}`
Requires a learner (`account_type == "user"`) token. Returns:
```json
{
  "section": { "id": 0, "course_id": 0, "section_number": "1.1", "title": "", "content": "" },
  "conversation": [ { "role": "user|assistant", "content": "" } ]
}
```
**Side effect**: if the learner has no `section_progress` row for this section yet,
one is inserted with `status = 'in_progress'`. Calling this endpoint is what starts a
section, not a separate "start" action.

## Teaching & evaluation

### `POST /api/chat`
Requires a learner token. Body: `{"section_id", "message"}`. Saves the learner's
message, calls teaching-service for a Socratic reply scoped to that section (up to the
teaching client's 60s RPC timeout), saves the reply, and returns `{"reply": "..."}`. If
teaching-service doesn't respond in time: `{"error": "Teaching service is unavailable,
please try again"}`. See [teaching-and-evaluation.md](teaching-and-evaluation.md) for
what the AI actually does with the conversation.

### `POST /api/sections/complete`
Requires a learner token. Body: `{"section_id"}`. Requires at least one saved message
(`{"error": "No conversation to evaluate"}` otherwise). Calls teaching-service to score
the transcript, writes the scores onto `section_progress`, and checks whether the
whole course is now done. Returns `{"completed": true, "credential_issued": bool}`.

## Learner: credentials

### `GET /api/my/credentials`
Requires a learner token. Returns `{"credentials": [{"course_title", "issued_at"},
...]}`.

## Employer

### `GET /api/employer/candidates`
Requires an employer token. Returns every learner in the system (not scoped to
applicants — this is a browse-all-candidates view) with their credentials and
completed-section scores:
```json
{ "candidates": [ {
  "id", "name", "email", "current_company",
  "credentials": [ { "course_title", "issued_at" } ],
  "section_scores": [ { "section_title", "speed", "explanation", "sharpness", "evidence" } ]
} ] }
```

### `POST /api/employer/jobs`
Requires an employer token. Body: `{"title", "description", "required_course_ids":
[1, 2]}`. Stores `required_course_ids` as a JSON string (see
[data-model.md](data-model.md#job_postings)). Returns `{"success": true}`.

### `GET /api/employer/jobs`
Requires an employer token. Returns only the calling employer's own postings, each
with candidates matched live against `required_course_ids` (a candidate must hold
*every* required course's credential):
```json
{ "jobs": [ { "id", "title", "description",
  "matched_candidates": [ { "id", "name", "email" } ] } ] }
```

## Admin

All admin routes require an admin token (`{"error": "Not authenticated"}` otherwise,
same as everywhere else — including for a valid learner/employer token, since account
type is checked strictly).

### `GET /api/admin/users`
Returns every learner with rollup counts: `{"users": [{"id", "name", "email",
"current_company", "completed_sections", "credentials_count"}, ...]}`, sorted by name.

### `GET /api/admin/users/{user_id}`
Full detail view backing the admin console's per-learner page: profile fields plus
every course/section with per-section status, scores, evidence, timestamps, and the
**full conversation transcript** for that section:
```json
{
  "user": { "id", "name", "email", "education", "experience", "current_company", "certifications" },
  "courses": [ { "id", "title", "sections": [ {
    "id", "section_number", "title", "status",
    "speed_score", "explanation_score", "question_sharpness_score", "evidence",
    "started_at", "completed_at",
    "conversation": [ { "role", "content" } ]
  } ] } ]
}
```

### `POST /api/admin/users/{user_id}/sections/{section_id}/override`
Body: `{"speed_score", "explanation_score", "question_sharpness_score", "evidence"?}`
(`evidence` defaults to `"Manually overridden by admin."`). Force-completes one
section with admin-supplied scores, bypassing teaching-service entirely, then checks
credential issuance. Returns `{"completed": true, "credential_issued": bool}`.

### `POST /api/admin/users/{user_id}/sections/bulk_override`
Same as above but for many sections at once. Body adds `"section_ids": [1, 2, ...]`
in place of a single `section_id`, and applies the *same* three scores + evidence to
all of them. Returns `{"completed": <count>, "credentials_issued": <count>}`.
`{"error": "No sections selected"}` if `section_ids` is empty.

### `POST /api/admin/users/{user_id}/sections/bulk_revert`
Body: `{"section_ids": [1, 2, ...]}`. Deletes `section_progress` for each (back to
`not_started`) and deletes any `credentials` row for a course that had a section
reverted. Returns `{"reverted": <count>, "credentials_revoked": <count>}`. See
[data-model.md](data-model.md#admin-overrides-and-reverts) for exactly what gets
deleted.

## Not exposed over HTTP

`generate_courses.py` (course/section seeding) and `create_admin.py` (admin
provisioning) are one-off scripts run directly, not API routes — see
[local-development.md](local-development.md).
