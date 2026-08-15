#!/usr/bin/env bash
# Talent Bridge — one-shot local setup and run (Linux/macOS/Git Bash).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
else
    PYTHON=python
fi

# 1. Virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv .venv
fi

if [ -f ".venv/bin/python" ]; then
    VENV_PY=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    VENV_PY=".venv/Scripts/python.exe"
else
    echo "Could not find a python executable inside .venv" >&2
    exit 1
fi

# 2. Dependencies
echo "Installing dependencies..."
"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet -r requirements.txt

# 3. .env
if [ ! -f ".env" ]; then
    echo "Creating .env (fill in ANTHROPIC_API_KEY before chatting or seeding courses)..."
    echo "ANTHROPIC_API_KEY=" > .env
fi

# 4. Local DB path for dev (production still defaults to /opt/talentbridge/data/talentbridge.db)
export TALENTBRIDGE_DB_PATH="$(pwd)/data/talentbridge.db"
mkdir -p data

# 5. Schema
if [ ! -f "$TALENTBRIDGE_DB_PATH" ]; then
    echo "Initializing database schema at $TALENTBRIDGE_DB_PATH..."
    "$VENV_PY" -c "import os, sqlite3; conn = sqlite3.connect(os.environ['TALENTBRIDGE_DB_PATH']); conn.executescript(open('schema.sql').read()); conn.commit()"
fi

# 6. Seed courses if the table is empty
COURSE_COUNT="$("$VENV_PY" -c "import os, sqlite3; conn = sqlite3.connect(os.environ['TALENTBRIDGE_DB_PATH']); print(conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0])")"
if [ "$COURSE_COUNT" -eq 0 ]; then
    if grep -q "ANTHROPIC_API_KEY=." .env 2>/dev/null; then
        echo "Seeding courses (this calls the Anthropic API)..."
        "$VENV_PY" generate_courses.py
    else
        echo "Skipping course seeding: set ANTHROPIC_API_KEY in .env, then run '$VENV_PY generate_courses.py' manually."
    fi
fi

# 7. Run
echo "Starting server at http://127.0.0.1:8000 ..."
"$VENV_PY" -m uvicorn main:app --reload
