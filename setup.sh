#!/usr/bin/env bash
# Talent Bridge — one-shot local setup and run via Docker Compose (Linux/macOS/Git Bash).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

# 1. Docker Compose availability
if ! docker compose version >/dev/null 2>&1; then
    echo "Docker (with Compose v2) is required. Install Docker and try again." >&2
    exit 1
fi

# 2. .env
if [ ! -f ".env" ]; then
    echo "Creating .env (fill in OPENROUTER_KEY, TURSO_DATABASE_URL, TURSO_AUTH_TOKEN before running)..."
    printf 'OPENROUTER_KEY=\nTURSO_DATABASE_URL=\nTURSO_AUTH_TOKEN=\n' > .env
fi

# 3. Build and run the gateway (the app talks to a remote Turso database, so
#    there's no local data directory to bind-mount anymore)
echo "Building and starting the gateway..."
echo "Gateway will be available at http://127.0.0.1:8000 once the container is up."

if ! grep -q "OPENROUTER_KEY=." .env 2>/dev/null || ! grep -q "TURSO_DATABASE_URL=." .env 2>/dev/null; then
    echo "Note: OPENROUTER_KEY / TURSO_DATABASE_URL / TURSO_AUTH_TOKEN are not all set in .env yet — the app will fail to start until they are."
fi
echo "Once your .env is filled in, seed courses (once) with:"
echo "    python generate_courses.py"

docker compose up --build
