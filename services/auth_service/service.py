"""
Talent Bridge Auth Service — handles both learner and employer accounts,
completely separate account types with their own tables.
"""

import bcrypt
import os
import secrets
import sqlite3
from datetime import datetime, timezone

_DB_PATH = os.getenv("TALENTBRIDGE_DB_PATH", "/opt/talentbridge/data/talentbridge.db")


def _get_db():
    return sqlite3.connect(_DB_PATH, check_same_thread=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def signup_user(email, password, name, education, experience, current_company, certifications):
    db = _get_db()
    existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing is not None:
        raise ValueError("An account with this email already exists")

    now = datetime.now(timezone.utc).isoformat()
    cursor = db.execute(
        "INSERT INTO users (email, password_hash, name, education, experience, current_company, certifications, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (email, hash_password(password), name, education, experience, current_company, certifications, now)
    )
    user_id = cursor.lastrowid
    db.commit()

    token = _create_token(db, "user", user_id)
    return {"account_id": user_id, "account_type": "user", "token": token}


def login_user(email, password):
    db = _get_db()
    row = db.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        raise ValueError("Invalid email or password")
    account_id, password_hash = row
    if not verify_password(password, password_hash):
        raise ValueError("Invalid email or password")
    token = _create_token(db, "user", account_id)
    return {"account_id": account_id, "account_type": "user", "token": token}


def signup_employer(email, password, company_name, contact_name):
    db = _get_db()
    existing = db.execute("SELECT id FROM employers WHERE email = ?", (email,)).fetchone()
    if existing is not None:
        raise ValueError("An account with this email already exists")

    now = datetime.now(timezone.utc).isoformat()
    cursor = db.execute(
        "INSERT INTO employers (email, password_hash, company_name, contact_name, created_at) VALUES (?, ?, ?, ?, ?)",
        (email, hash_password(password), company_name, contact_name, now)
    )
    account_id = cursor.lastrowid
    db.commit()

    token = _create_token(db, "employer", account_id)
    return {"account_id": account_id, "account_type": "employer", "token": token}


def login_employer(email, password):
    db = _get_db()
    row = db.execute("SELECT id, password_hash FROM employers WHERE email = ?", (email,)).fetchone()
    if row is None:
        raise ValueError("Invalid email or password")
    account_id, password_hash = row
    if not verify_password(password, password_hash):
        raise ValueError("Invalid email or password")
    token = _create_token(db, "employer", account_id)
    return {"account_id": account_id, "account_type": "employer", "token": token}


def login_admin(email, password):
    db = _get_db()
    row = db.execute("SELECT id, password_hash FROM admins WHERE email = ?", (email,)).fetchone()
    if row is None:
        raise ValueError("Invalid email or password")
    account_id, password_hash = row
    if not verify_password(password, password_hash):
        raise ValueError("Invalid email or password")
    token = _create_token(db, "admin", account_id)
    return {"account_id": account_id, "account_type": "admin", "token": token}


def _create_token(db, account_type, account_id):
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        "INSERT INTO auth_tokens (token, account_type, account_id, created_at) VALUES (?, ?, ?, ?)",
        (token, account_type, account_id, now)
    )
    db.commit()
    return token


def get_account_from_token(token):
    db = _get_db()
    row = db.execute(
        "SELECT account_type, account_id FROM auth_tokens WHERE token = ?", (token,)
    ).fetchone()
    if row is None:
        return None
    account_type, account_id = row

    if account_type == "user":
        user = db.execute(
            "SELECT id, email, name, education, experience, current_company, certifications FROM users WHERE id = ?",
            (account_id,)
        ).fetchone()
        if user is None:
            return None
        return {
            "account_type": "user", "id": user[0], "email": user[1], "name": user[2],
            "education": user[3], "experience": user[4], "current_company": user[5], "certifications": user[6]
        }
    elif account_type == "employer":
        employer = db.execute(
            "SELECT id, email, company_name, contact_name FROM employers WHERE id = ?",
            (account_id,)
        ).fetchone()
        if employer is None:
            return None
        return {
            "account_type": "employer", "id": employer[0], "email": employer[1],
            "company_name": employer[2], "contact_name": employer[3]
        }
    elif account_type == "admin":
        admin = db.execute(
            "SELECT id, email, name FROM admins WHERE id = ?",
            (account_id,)
        ).fetchone()
        if admin is None:
            return None
        return {"account_type": "admin", "id": admin[0], "email": admin[1], "name": admin[2]}
    else:
        return None
