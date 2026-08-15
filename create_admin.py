"""
One-off script: creates a Talent Bridge admin account directly in the DB.

There is deliberately no public /api/auth/signup/admin endpoint — the admin
console exposes every learner's private conversation and scenario history,
so admin accounts are provisioned out-of-band instead of by self-signup.

Usage: python create_admin.py <email> <password> <name>
"""

import argparse
import os
from datetime import datetime, timezone

import bcrypt
import libsql
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description="Create a Talent Bridge admin account")
parser.add_argument("email")
parser.add_argument("password")
parser.add_argument("name")
args = parser.parse_args()

db = libsql.connect(os.environ["TURSO_DATABASE_URL"], auth_token=os.environ["TURSO_AUTH_TOKEN"])

_schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
db.executescript(open(_schema_path).read())

existing = db.execute("SELECT id FROM admins WHERE email = ?", (args.email,)).fetchone()
if existing is not None:
    raise SystemExit(f"An admin with email {args.email} already exists")

password_hash = bcrypt.hashpw(args.password.encode(), bcrypt.gensalt()).decode()
now = datetime.now(timezone.utc).isoformat()
db.execute(
    "INSERT INTO admins (email, password_hash, name, created_at) VALUES (?, ?, ?, ?)",
    (args.email, password_hash, args.name, now)
)
db.commit()
print(f"Admin account created for {args.email}")
