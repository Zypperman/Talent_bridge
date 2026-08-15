#!/bin/sh
set -e

python -c "import os, libsql; libsql.connect(os.environ['TURSO_DATABASE_URL'], auth_token=os.environ['TURSO_AUTH_TOKEN']).executescript(open('schema.sql').read())"

exec uvicorn gateway.main:app --host 0.0.0.0 --port 8000
