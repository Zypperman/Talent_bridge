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
    echo "Creating .env (fill in OPENROUTER_KEY before chatting or seeding courses)..."
    echo "OPENROUTER_KEY=" > .env
fi

# 3. Data directory (bind-mounted into the gateway/auth-service/teaching-service containers)
mkdir -p data

# 4. Build and run every service (gateway, auth-service, teaching-service, redis)
echo "Building and starting services..."
echo "Gateway will be available at http://127.0.0.1:8000 once containers are up."

if ! grep -q "OPENROUTER_KEY=." .env 2>/dev/null; then
    echo "Note: OPENROUTER_KEY is not set in .env yet, so teaching-service will fail to answer chats/evaluations until you set it and restart."
fi
echo "Once OPENROUTER_KEY is set and containers are running, seed courses (once) with:"
echo "    docker compose run --rm teaching-service python generate_courses.py"

docker compose up --build
