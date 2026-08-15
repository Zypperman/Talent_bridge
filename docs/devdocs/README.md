# Talent Bridge — Developer Documentation

This folder is the deep-dive companion to the top-level [README.md](../README.md). The
top-level README covers *what the product is* and *how to run it*; these docs cover
*how it's built* — the pieces, the protocols between them, and where to look when you
need to change something.

Read them in whichever order matches what you're doing:

| Doc | Read this when you need to... |
| --- | --- |
| [architecture.md](architecture.md) | Understand the overall system shape: gateway, services, Redis, DB, how a request flows end to end. Start here if you're new. |
| [data-model.md](data-model.md) | Understand the SQLite schema, table relationships, and how progress/credentials/scores are derived. |
| [api-reference.md](api-reference.md) | Look up a specific `/api/*` endpoint's request/response shape, auth requirements, and error cases. |
| [auth-and-accounts.md](auth-and-accounts.md) | Work on signup/login/tokens, or understand the three account types (user, employer, admin). |
| [teaching-and-evaluation.md](teaching-and-evaluation.md) | Change the Socratic teaching prompt, the evaluation rubric, or the AI model/provider. |
| [frontend.md](frontend.md) | Modify `static/index.html` or `static/admin.html` — how the no-build vanilla-JS frontends are structured. |
| [local-development.md](local-development.md) | Run a single piece in isolation, seed courses, create an admin, or debug the RPC layer directly. |

## The one-paragraph version

Talent Bridge is three Python processes (a FastAPI **gateway** plus two headless
**auth** and **teaching** services) that talk to each other over **Redis** request/reply
queues, all reading and writing one shared **SQLite** file. The gateway is the only
thing that speaks HTTP; it owns `/api/*` and serves the two static, build-free HTML/JS
frontends (`static/index.html` for learners/employers, `static/admin.html` for admins).
Course content is Socratic-taught and scored by Claude via OpenRouter. See
[architecture.md](architecture.md) for the full picture.

## Source of truth

These docs describe the code as of this writing. When in doubt, the code wins —
in particular:
- [gateway/main.py](../gateway/main.py) is the complete list of HTTP routes.
- [schema.sql](../schema.sql) is the complete list of tables/columns.
- [common/rpc.py](../common/rpc.py) is the complete RPC wire protocol.

The removed incident-simulation sandbox is documented separately in
[docs/Sandbox_Architecture.md](../docs/Sandbox_Architecture.md) and
[docs/no-sim-justification.md](../docs/no-sim-justification.md) — it's not part of the
running system and isn't covered here.
