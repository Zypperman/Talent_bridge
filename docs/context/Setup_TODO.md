# Setup TODO

What's actually left to get this running, checked against this machine's current state (Windows 11, checked 2026-08-15). Not a feature roadmap.

The sandbox service (Phases 2–4 in earlier versions of this doc) has been removed from the codebase — the mock-fidelity spike found that a convincing simulation needs vendor-provisioned software, not more local tooling. See [docs/Sandbox_Architecture.md](Sandbox_Architecture.md) and [docs/no-sim-justification.md](no-sim-justification.md).

## Phase 1 — Run the app itself

- [x] **Docker Desktop** — installed, daemon reachable (`docker info` succeeds), Compose v2.38 present.
- [x] **Python 3** — 3.13.9 on PATH.
- [x] **SQLite** — already present, nothing to install. Python's stdlib `sqlite3` module reports `3.51.0`, and the `sqlite3` CLI is also on PATH (useful for poking at `data/talentbridge.db` directly: `sqlite3 data/talentbridge.db ".tables"`).
- [ ] **`OPENROUTER_KEY` in `.env`** — currently missing/empty. Without it, `teaching-service` starts but every Claude call (chat + evaluation + `generate_courses.py`) fails. Get a key at [openrouter.ai/keys](https://openrouter.ai/keys) and add `OPENROUTER_KEY=...` to `.env`.
- [ ] **Seed the courses table** (once `OPENROUTER_KEY` is set) — it's currently empty until this runs:
  ```bash
  docker compose run --rm teaching-service python generate_courses.py
  ```
- [ ] **Bring the stack up**:
  ```bash
  docker compose up --build
  ```
  Gateway comes up at `http://127.0.0.1:8000`; it applies `schema.sql` automatically on start.

Manual (no Docker) path is documented in the README, but Docker is the faster route here since it's already installed and working.
