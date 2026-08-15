# Talent Bridge

**Proving real understanding, not content consumption.**

Talent Bridge is a training and credentialing platform for Batam's data-center and tech-operations skills gap. Instead of a video course and a multiple-choice quiz, learners work through course sections in a real Socratic conversation with an AI instructor. They only advance once they can explain the concept back in their own words — and every conversation is scored on speed, explanation quality, and question sharpness. Employers don't see a "Certificate of Completion"; they see a credential backed by an evidence trail, and can match it directly against job requirements.

## The problem

Platforms like YouTube, Udemy, and Coursera have great expert content — that's not the gap. The gap is what happens *after* the content: a quiz and a certificate that only prove someone watched the videos, not that they understood the material. Employers have no reliable way to tell the difference.

## How it works

1. **Structured courses** — each course is broken into sequential sections (1.1, 1.2, 1.3, ...), each building on the last. Learners can't skip ahead.
2. **Socratic teaching** — to move to the next section, a learner has a real conversation with an AI instructor scoped strictly to that section's content, explaining concepts back in their own words.
3. **Transparent evaluation** — every conversation is scored on three parameters: how quickly genuine understanding was reached, how well the learner explained it back, and how sharp their own questions were. Scores are backed by quoted evidence from the transcript, not opaque numbers.
4. **Earned credentials** — a course credential is only issued once every section is genuinely completed.
5. **Evidence-based hiring** — employers post jobs with required course credentials and instantly see every candidate who has genuinely earned them, along with the underlying scores and evidence.

Course content itself is AI-drafted and then human-reviewed for technical accuracy before it goes live.

## Features

- Separate learner and employer accounts with token-based auth
- Section-by-section course progression with per-user progress tracking
- Claude-powered Socratic teaching (via OpenRouter), scoped to one section at a time
- Automated, evidence-backed evaluation (speed / explanation / question sharpness)
- Credential issuance on full course completion
- Employer dashboard: browse candidates with their credentials and scores
- Job postings with automatic matching against required course credentials
- Admin console for monitoring every learner's module conversation history

### Not implemented: incident-simulation sandbox

An earlier design ([docs/Sandbox_Architecture.md](docs/Sandbox_Architecture.md)) scaffolded a sandbox service that would provision per-learner mock data-center environments (Kubernetes + Terraform-injected faults) for hands-on incident exercises. That implementation has been removed. A convincing simulation turns out to require the real vendor software — most storage/network platforms have no public simulator, and generated-fake CLI output doesn't survive scrutiny from anyone who knows the real tool — which means enterprise accounts and vendor collaboration, not more engineering time. See [docs/no-sim-justification.md](docs/no-sim-justification.md) for the full reasoning. The architecture doc is kept as a reference for a future revival that starts with vendor partnerships.

## Tech stack

| Layer | Technology | Why |
| --- | --- | --- |
| App | Python + FastAPI | A single process owns the `/api/*` surface, the frontend, and the auth/teaching business logic (imported as plain modules — no RPC hop) |
| AI engine | Claude, via [OpenRouter](https://openrouter.ai/) | Powers Socratic teaching, post-conversation evaluation, and initial course content drafting; routed through OpenRouter's OpenAI-compatible API so the model/provider is a config value, not a hardcoded SDK dependency |
| Database | [Turso](https://turso.tech/) (libSQL, SQLite-compatible) | Same SQL dialect and schema as plain SQLite, but reachable over the network — required once the app runs as stateless serverless functions instead of one long-lived process with a local file |
| Frontend | Plain HTML/CSS/JavaScript | No build step, one file, nothing to break live during a demo |
| Deployment | Vercel (serverless) or Docker Compose | One FastAPI app runs unchanged either way — `vercel deploy` or `docker compose up` |

Earlier versions split auth and teaching into standalone processes talking to the
gateway over Redis request/reply queues, for process isolation. That model doesn't
run on serverless platforms (no persistent processes, no Redis server), and since this
app is small enough that the isolation wasn't paying for itself, it was collapsed into
one process — see [Deploying to Vercel](#deploying-to-vercel).

## Project structure

```text
Talent_bridge/
├── gateway/
│   ├── main.py               # FastAPI app: all API routes, calls services/* directly, serves static/ as the frontend
│   ├── entrypoint.sh          # Applies schema.sql (to Turso) then starts uvicorn
│   └── Dockerfile
├── services/
│   ├── auth_service/
│   │   └── service.py         # Signup/login + token auth business logic, imported directly by gateway/main.py
│   └── teaching_service/
│       └── service.py         # Socratic teaching replies + section evaluation via Claude, imported directly by gateway/main.py
├── generate_courses.py       # One-off script: AI-drafts course sections and seeds the DB
├── create_admin.py           # One-off script: creates an admin account (no public signup endpoint)
├── static/
│   ├── index.html            # Learner/employer frontend (single page, no build tools)
│   └── admin.html            # Admin console: per-learner conversation history
├── schema.sql                 # SQLite/libSQL table definitions (idempotent, applied automatically on startup)
├── docker-compose.yml          # Single `gateway` container, for local/self-hosted use
├── pyproject.toml              # Points Vercel's Python runtime at gateway/main.py's `app`
├── vercel.json                  # Vercel function config (maxDuration for the OpenRouter calls)
├── requirements.txt            # Single dependency list — used by Vercel, Docker, and local `uvicorn`
├── setup.sh / setup.ps1        # One-shot local setup and run via Docker Compose (bash / PowerShell)
└── docs/                     # Product requirements, architecture notes, pitch materials — including
                               # Sandbox_Architecture.md and no-sim-justification.md for the removed sandbox feature
```

## Setup

### Prerequisites

- A [Turso](https://turso.tech/) database (free tier is fine) — this is the app's only datastore
- An [OpenRouter API key](https://openrouter.ai/keys)
- [Docker](https://www.docker.com/) with Compose v2, if running locally via Docker

### Quick start (Docker)

`setup.sh` (Linux/macOS/Git Bash) and `setup.ps1` (Windows PowerShell) each do the full local setup: create `.env` if missing, then build and start the gateway with Docker Compose.

```bash
./setup.sh
```

```powershell
.\setup.ps1
```

The gateway comes up at `http://127.0.0.1:8000`. On startup it applies `schema.sql` to your Turso database automatically (safe to run repeatedly — every statement is `CREATE ... IF NOT EXISTS`).

Fill in `OPENROUTER_KEY`, `TURSO_DATABASE_URL`, and `TURSO_AUTH_TOKEN` in `.env` before starting, or the container will fail to connect. Once it's running, seed the courses table (once, if empty):

```bash
python generate_courses.py
```

### Admin console

There's no public signup for admin accounts — the console shows every learner's private conversation transcripts, so admins are provisioned out-of-band with `create_admin.py` rather than through the API:

```bash
python create_admin.py you@example.com yourpassword "Your Name"
```

Then log in at `http://127.0.0.1:8000/admin.html`. The console lists every learner and, per learner, their full section-by-section conversation history (with scores/evidence).

### Manual setup (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
printf 'OPENROUTER_KEY=your-api-key-here\nTURSO_DATABASE_URL=libsql://your-db.turso.io\nTURSO_AUTH_TOKEN=your-token\n' > .env
python -c "import os, libsql; from dotenv import load_dotenv; load_dotenv(); libsql.connect(os.environ['TURSO_DATABASE_URL'], auth_token=os.environ['TURSO_AUTH_TOKEN']).executescript(open('schema.sql').read())"
python generate_courses.py   # seeds courses, requires OPENROUTER_KEY
uvicorn gateway.main:app --reload
```

The API is served under `/api/*`, and the frontend at `static/index.html` is mounted at `/`.

## Deploying to Vercel

The app is a single FastAPI app (`gateway/main.py`), so it deploys to Vercel as one
serverless function; `pyproject.toml` points Vercel at it and `vercel.json` raises the
function's timeout to 60s to give OpenRouter/Claude room to respond on the chat and
evaluation endpoints.

1. **Create a Turso database** (skip if you already have one from local setup):

   ```bash
   curl -sSfL https://get.tur.so/install.sh | bash   # or: brew install tursodatabase/tap/turso
   turso auth signup   # or `turso auth login` if you already have an account
   turso db create talent-bridge
   turso db show talent-bridge --url          # → TURSO_DATABASE_URL
   turso db tokens create talent-bridge       # → TURSO_AUTH_TOKEN
   turso db shell talent-bridge < schema.sql  # applies the schema (idempotent)
   ```

2. **Seed courses and create an admin account**, run once from your machine with
   `TURSO_DATABASE_URL` / `TURSO_AUTH_TOKEN` / `OPENROUTER_KEY` set in `.env`:

   ```bash
   python generate_courses.py
   python create_admin.py you@example.com yourpassword "Your Name"
   ```

3. **Deploy to Vercel**:

   ```bash
   npm i -g vercel
   vercel login
   vercel link                 # creates/links the Vercel project
   vercel env add OPENROUTER_KEY production
   vercel env add TURSO_DATABASE_URL production
   vercel env add TURSO_AUTH_TOKEN production
   vercel deploy --prod
   ```

   (Repeat the `vercel env add` commands for the `preview`/`development` environments
   too if you want `vercel dev` and preview deploys to work.)

Once deployed, the app is available at your `*.vercel.app` URL — `/` serves
`static/index.html`, `/admin.html` serves the admin console, and `/api/*` is the same
API described below.

## Slides (Marp deck)

The product slide deck lives in `slides/` as a self-contained npm project (requires [Node.js](https://nodejs.org/)):

```bash
cd slides
npm install
npm run preview   # live-reloading preview at http://localhost:8080
```

Edit `slides/slides.md` and the preview updates automatically. To export a static file instead:

```bash
npm run build:html   # slides/dist/slides.html
npm run build:pdf     # slides/dist/slides.pdf
npm run build:pptx    # slides/dist/slides.pptx
```

The deck's content plan (slide-by-slide outline the deck is built from) lives at [docs/slide_summary.md](docs/slide_summary.md).

## API overview

| Endpoint | Description |
| --- | --- |
| `POST /api/auth/signup/user` / `login/user` | Learner signup and login |
| `POST /api/auth/signup/employer` / `login/employer` | Employer signup and login |
| `POST /api/auth/login/admin` | Admin login (no public signup — see [Admin console](#admin-console)) |
| `GET /api/auth/me` | Current authenticated account |
| `GET /api/courses` | List all courses |
| `GET /api/courses/{course_id}/sections` | List a course's sections with progress status |
| `GET /api/sections/{section_id}` | Section content + conversation history |
| `POST /api/chat` | Send a message to the AI instructor for a section |
| `POST /api/sections/complete` | Evaluate the conversation and mark a section complete |
| `GET /api/my/credentials` | Learner's earned credentials |
| `GET /api/employer/candidates` | Employer view of all candidates, credentials, and scores |
| `POST /api/employer/jobs` / `GET /api/employer/jobs` | Create and list job postings with matched candidates |
| `GET /api/admin/users` | Admin: list all learners with progress/credential summary counts |
| `GET /api/admin/users/{user_id}` | Admin: full detail — profile, per-section conversation history and scores |

## License

MIT — see [LICENSE](LICENSE).
