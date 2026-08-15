#!/bin/sh
set -e

python -c "import os, sqlite3; sqlite3.connect(os.environ['TALENTBRIDGE_DB_PATH']).executescript(open('/app/schema.sql').read())"

exec uvicorn main:app --host 0.0.0.0 --port 8000
