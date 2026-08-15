# Frontend

Two single-file, no-build vanilla-JS pages, served directly off disk by the gateway's
`StaticFiles` mount (`app.mount("/", StaticFiles(directory="static", html=True))` in
[gateway/main.py](../gateway/main.py)). No React/Vue, no bundler, no npm install for
either page — edit the HTML file and reload the browser. (The unrelated `slides/`
directory *does* use npm/Marp for the pitch deck — see the top-level
[README](../README.md#slides-marp-deck) — but that's a separate project, not part of
the running app.)

## Shared pattern

Both `static/index.html` (learners + employers) and `static/admin.html` (admin
console) use the identical hand-rolled architecture:

- A single mutable `state` object (`view`, `token`, and page-specific fields like
  `courses`/`candidates`/`currentUser`).
- `api(path, method, body)` — a thin `fetch` wrapper that attaches
  `Authorization: Bearer <token>` from `state.token` and always parses the response as
  JSON (errors come back as `{"error": ...}` in a 200, not as thrown exceptions — see
  [api-reference.md](api-reference.md#conventions)).
- `render()` — clears `#app` and calls one `render<View>()` function based on
  `state.view`, which returns a DOM node built via a small `el(html)` helper
  (`el` just does `document.createElement('div'); d.innerHTML = html; return
  d.firstElementChild`) — i.e. HTML is built with template strings and interpolation,
  not a virtual DOM or templating engine.
- `nav(view)` — sets `state.view` and re-renders. There's no client-side router/URL
  sync — the browser URL never changes as you navigate between "pages"; a refresh
  always lands back on the initial view (`landing`/`login`) and relies on the token in
  `localStorage` plus `checkAuth()` to fast-forward past it.
- Auth persistence: token + account type are stored in `localStorage`
  (`tb_token`/`tb_type` for `index.html`, `tb_admin_token` for `admin.html` — separate
  keys, so being logged into the learner/employer app and the admin console at the
  same time in one browser doesn't conflict). On load, `init()` checks for a stored
  token, calls `GET /api/auth/me` to validate it, and jumps straight to the
  appropriate logged-in view if valid, or drops back to the login/landing view
  (`logout()`) if not.

Because there's no build step, **be careful with unescaped user content** — most
interpolations in these files go straight into `innerHTML`. `admin.html` escapes `<`
in conversation content before display (`m.content.replace(/</g, '&lt;')`) since
transcripts can contain arbitrary learner text; `index.html`'s chat view does not
escape message content at all. Keep this in mind before adding new fields that
surface arbitrary user input.

## `static/index.html` — learner & employer app

Views (`state.view` values), all defined as `render<Name>()` functions in the file:

| View | Purpose |
| --- | --- |
| `landing` | Role choice: "I'm here to learn" vs "I'm hiring". |
| `user_login` / `user_signup` | Learner auth forms → `nav('courses')` on success. |
| `employer_login` / `employer_signup` | Employer auth forms → `nav('employer_candidates')` on success. |
| `courses` | Lists all courses (`GET /api/courses`); click → `nav('sections')`. |
| `sections` | Lists a course's sections with status badges (`GET /api/courses/{id}/sections`); click → `nav('section_chat')`. |
| `section_chat` | The chat UI: loads history (`GET /api/sections/{id}`), sends messages (`POST /api/chat`), and has the "Mark Section Complete" button (`POST /api/sections/complete`). |
| `my_credentials` | Learner's earned credentials (`GET /api/my/credentials`). |
| `employer_candidates` | Browse-all-candidates view (`GET /api/employer/candidates`). |
| `employer_jobs` | Post a job (checkbox list of required courses) and list existing postings with live-matched candidates (`GET`/`POST /api/employer/jobs`). |

Notable implementation details:
- `renderSectionChat()` optimistically appends the learner's own message to the chat
  box *before* the `POST /api/chat` response comes back, then appends the assistant
  reply once it arrives — there's no loading indicator while waiting.
- Opening a section (`renderSections` → click → `nav('section_chat')` → `load()`
  inside `renderSectionChat`) is what triggers the `section_progress` "in_progress"
  row server-side, per `GET /api/sections/{id}`'s side effect (see
  [data-model.md](data-model.md)).

## `static/admin.html` — admin console

Views: `login` → `users` (all learners, click one) → `user_detail` (one learner's full
course/section breakdown with transcripts).

The bulk of this file's complexity is in `renderUserDetail()`, which implements:
- **Per-section `<details>` panels**: each section shows its status badge, scores +
  evidence if completed, the full transcript, and a nested "Override scores" /
  "Mark complete (override)" panel with its own score inputs
  (`POST /api/admin/users/{uid}/sections/{sid}/override`).
- **Multi-select bulk actions**: a checkbox per section feeds `state.selectedSections`
  (a `Map` of `id → label`). A fixed bottom bar appears once anything is selected,
  offering "Review & mark complete" (bulk override, one shared set of scores applied
  to every selected section) or "Revert selected to not started" (bulk revert). Both
  paths route through a shared `openModal({title, bodyHtml, confirmLabel, onConfirm})`
  helper that renders a confirmation dialog, lists the affected sections by name, and
  only calls the API once the admin confirms — since bulk override/revert are
  destructive-ish (they overwrite real evaluation results or delete progress +
  revoke credentials), the confirmation step is deliberate, not boilerplate.
- **Single-section revert**: same `confirmRevert([...])` helper, called with a
  one-item list, reachable from an individual section's "Revert to not started" link.

If you're adding a new admin bulk action, `openModal` + the `state.selectedSections`
map is the existing pattern to extend rather than building a new selection mechanism.
