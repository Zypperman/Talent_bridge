-- Talent Bridge database schema.
-- Inferred from the queries in main.py and services/*.py — there was no
-- schema file in the repo, so this reconstructs the tables those modules
-- expect. Safe to re-run: every statement is idempotent.

CREATE TABLE IF NOT EXISTS users (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    email             TEXT NOT NULL UNIQUE,
    password_hash     TEXT NOT NULL,
    name              TEXT NOT NULL,
    education         TEXT,
    experience        TEXT,
    current_company   TEXT,
    certifications    TEXT,
    created_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    company_name   TEXT NOT NULL,
    contact_name   TEXT NOT NULL,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_tokens (
    token         TEXT PRIMARY KEY,
    account_type  TEXT NOT NULL,   -- 'user' or 'employer'
    account_id    INTEGER NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    slug           TEXT NOT NULL UNIQUE,
    title          TEXT NOT NULL,
    description    TEXT,
    display_order  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id       INTEGER NOT NULL REFERENCES courses(id),
    section_number  TEXT NOT NULL,
    title           TEXT NOT NULL,
    content         TEXT NOT NULL,
    display_order   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    section_id  INTEGER NOT NULL REFERENCES sections(id),
    role        TEXT NOT NULL,     -- 'user' or 'assistant'
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS section_progress (
    user_id                   INTEGER NOT NULL REFERENCES users(id),
    section_id                INTEGER NOT NULL REFERENCES sections(id),
    status                    TEXT NOT NULL DEFAULT 'not_started', -- 'in_progress' | 'completed'
    speed_score               REAL,
    explanation_score         REAL,
    question_sharpness_score  REAL,
    evidence                  TEXT,
    started_at                TEXT,
    completed_at              TEXT,
    PRIMARY KEY (user_id, section_id)
);

CREATE TABLE IF NOT EXISTS credentials (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    course_id   INTEGER NOT NULL REFERENCES courses(id),
    issued_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_postings (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id           INTEGER NOT NULL REFERENCES employers(id),
    title                 TEXT NOT NULL,
    description           TEXT,
    required_course_ids   TEXT NOT NULL, -- JSON array, e.g. "[1, 2]"
    created_at            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sandbox_sessions (
    id                  TEXT PRIMARY KEY,          -- session_id (uuid4 hex)
    scenario_id         TEXT NOT NULL,
    user_id             INTEGER NOT NULL REFERENCES users(id),
    namespace           TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'provisioning', -- provisioning|ready|verifying|passed|failed|error|destroyed
    access_command      TEXT,
    verification_logs   TEXT,
    error_message       TEXT,
    created_at          TEXT NOT NULL,
    verified_at         TEXT,
    destroyed_at        TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_user_section ON messages(user_id, section_id);
CREATE INDEX IF NOT EXISTS idx_sections_course ON sections(course_id);
CREATE INDEX IF NOT EXISTS idx_credentials_user ON credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_sessions_user ON sandbox_sessions(user_id);
