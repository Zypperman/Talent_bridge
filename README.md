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

## Tech stack

| Layer | Technology | Why |
| --- | --- | --- |
| Gateway | Python + FastAPI | Owns the `/api/*` surface and the frontend; talks to auth/teaching over RPC |
| Auth service | Python, standalone process | Signup/login + token auth for learners and employers, isolated from the rest of the app |
| Teaching service | Python, standalone process | Socratic teaching replies + section evaluation via Claude, isolated so an AI-call slowdown can't block auth or course browsing |
| Service messaging | Redis (request/reply queues) | Gateway and services run as independent processes/containers and talk over a queue instead of function calls |
| AI engine | Claude, via [OpenRouter](https://openrouter.ai/) | Powers Socratic teaching, post-conversation evaluation, and initial course content drafting; routed through OpenRouter's OpenAI-compatible API so the model/provider is a config value, not a hardcoded SDK dependency |
| Database | SQLite | Single shared file, no separate DB server — simple and reliable at this scale; bind-mounted into every container that needs it |
| Frontend | Plain HTML/CSS/JavaScript | No build step, one file, nothing to break live during a demo |
| Deployment | Docker Compose | Each service builds and runs as its own container; `docker compose up` brings up the whole system |

## Project structure

```text
Talent_bridge/
├── gateway/
│   ├── main.py               # FastAPI app: all API routes, serves static/ as the frontend
│   ├── entrypoint.sh          # Applies schema.sql then starts uvicorn
│   ├── Dockerfile
│   └── requirements.txt
├── services/
│   ├── auth_service/
│   │   ├── service.py         # Signup/login + token auth business logic
│   │   ├── worker.py          # RPC worker: serves auth requests from the `queue:auth` Redis queue
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── teaching_service/
│       ├── service.py         # Socratic teaching replies + section evaluation via Claude
│       ├── worker.py          # RPC worker: serves requests from the `queue:teaching` Redis queue
│       ├── Dockerfile
│       └── requirements.txt
├── common/
│   └── rpc.py                 # Shared Redis request/reply RPC client (gateway) + worker loop (services)
├── generate_courses.py       # One-off script: AI-drafts course sections and seeds the DB
├── static/
│   └── index.html            # Frontend (single page, no build tools)
├── schema.sql                 # SQLite table definitions (idempotent, applied automatically by the gateway container)
├── docker-compose.yml          # Orchestrates redis, auth-service, teaching-service, gateway
├── requirements.txt            # Convenience "everything" file for running components without Docker
├── setup.sh / setup.ps1        # One-shot local setup and run via Docker Compose (bash / PowerShell)
└── docs/                     # Product requirements, architecture notes, pitch materials
```

## Getting started

### Prerequisites

- [Docker](https://www.docker.com/) with Compose v2 (`docker compose ...`)
- An [OpenRouter API key](https://openrouter.ai/keys)

### Quick start

`setup.sh` (Linux/macOS/Git Bash) and `setup.ps1` (Windows PowerShell) each do the full local setup: create `.env` if missing, create the `data/` directory that's bind-mounted into the containers, then build and start every service with Docker Compose.

```bash
./setup.sh
```

```powershell
.\setup.ps1
```

The gateway comes up at `http://127.0.0.1:8000`. On startup it applies `schema.sql` to `data/talentbridge.db` automatically (safe to run repeatedly — every statement is `CREATE ... IF NOT EXISTS`).

If `.env` doesn't have `OPENROUTER_KEY` set yet, `teaching-service` will start but fail Claude calls — fill it in and re-run `docker compose up --build`. Once it's set and the containers are running, seed the courses table (once, if empty):

```bash
docker compose run --rm teaching-service python generate_courses.py
```

Every service reads `TALENTBRIDGE_DB_PATH` (set to `/data/talentbridge.db` inside the containers via `docker-compose.yml`) and `REDIS_URL` (set to `redis://redis:6379/0`) from the environment.

### Manual setup (without Docker)

Each piece can also run locally as a plain Python process — useful for quick iteration on one service. You'll need a local Redis instance (`redis-server`, or `docker run -p 6379:6379 redis:7-alpine`) and to run the gateway plus both services in separate terminals:

```bash
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
echo "OPENROUTER_KEY=your-api-key-here" > .env
export TALENTBRIDGE_DB_PATH="$(pwd)/data/talentbridge.db"   # $env:TALENTBRIDGE_DB_PATH = ... on Windows
export REDIS_URL="redis://localhost:6379/0"                 # $env:REDIS_URL = ... on Windows
export PYTHONPATH="$(pwd)"                                   # $env:PYTHONPATH = ... on Windows — lets gateway/ and services/*/ import common.rpc
mkdir -p data
python -c "import sqlite3; sqlite3.connect('data/talentbridge.db').executescript(open('schema.sql').read())"
python generate_courses.py   # seeds courses, requires OPENROUTER_KEY

# in three separate terminals (same env vars in each):
python services/auth_service/worker.py
python services/teaching_service/worker.py
uvicorn main:app --reload --app-dir gateway
```

The API is served under `/api/*`, and the frontend at `static/index.html` is mounted at `/`.

### Slides (Marp deck)

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
| `GET /api/auth/me` | Current authenticated account |
| `GET /api/courses` | List all courses |
| `GET /api/courses/{course_id}/sections` | List a course's sections with progress status |
| `GET /api/sections/{section_id}` | Section content + conversation history |
| `POST /api/chat` | Send a message to the AI instructor for a section |
| `POST /api/sections/complete` | Evaluate the conversation and mark a section complete |
| `GET /api/my/credentials` | Learner's earned credentials |
| `GET /api/employer/candidates` | Employer view of all candidates, credentials, and scores |
| `POST /api/employer/jobs` / `GET /api/employer/jobs` | Create and list job postings with matched candidates |

## License

MIT — see [LICENSE](LICENSE).
