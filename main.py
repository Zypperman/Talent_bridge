from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3, json
from datetime import datetime, timezone
from services import auth_service, teaching_service

DB_PATH = "/opt/talentbridge/data/talentbridge.db"
db = sqlite3.connect(DB_PATH, check_same_thread=False)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserSignupRequest(BaseModel):
    email: str
    password: str
    name: str
    education: str = ""
    experience: str = ""
    current_company: str = ""
    certifications: str = ""


class EmployerSignupRequest(BaseModel):
    email: str
    password: str
    company_name: str
    contact_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    section_id: int
    message: str


class CompleteSectionRequest(BaseModel):
    section_id: int


class JobPostingRequest(BaseModel):
    title: str
    description: str
    required_course_ids: list


def get_account(authorization: str | None):
    if authorization is None:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return auth_service.get_account_from_token(token)


def get_conversation(user_id, section_id):
    rows = db.execute(
        "SELECT role, content FROM messages WHERE user_id = ? AND section_id = ? ORDER BY id",
        (user_id, section_id)
    ).fetchall()
    return [{"role": r, "content": c} for r, c in rows]


def save_message(user_id, section_id, role, content):
    db.execute(
        "INSERT INTO messages (user_id, section_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, section_id, role, content, datetime.now(timezone.utc).isoformat())
    )
    db.commit()
@app.post("/api/auth/signup/user")
def signup_user(req: UserSignupRequest):
    try:
        return auth_service.signup_user(req.email, req.password, req.name, req.education, req.experience, req.current_company, req.certifications)
    except ValueError as e:
        return {"error": str(e)}

@app.post("/api/auth/login/user")
def login_user(req: LoginRequest):
    try:
        return auth_service.login_user(req.email, req.password)
    except ValueError as e:
        return {"error": str(e)}

@app.post("/api/auth/signup/employer")
def signup_employer(req: EmployerSignupRequest):
    try:
        return auth_service.signup_employer(req.email, req.password, req.company_name, req.contact_name)
    except ValueError as e:
        return {"error": str(e)}

@app.post("/api/auth/login/employer")
def login_employer(req: LoginRequest):
    try:
        return auth_service.login_employer(req.email, req.password)
    except ValueError as e:
        return {"error": str(e)}

@app.get("/api/auth/me")
def me(authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None:
        return {"error": "Not authenticated"}
    return {"account": account}

@app.get("/api/courses")
def list_courses():
    rows = db.execute("SELECT id, slug, title, description FROM courses ORDER BY display_order").fetchall()
    return {"courses": [{"id": r[0], "slug": r[1], "title": r[2], "description": r[3]} for r in rows]}

@app.get("/api/courses/{course_id}/sections")
def list_sections(course_id: int, authorization: str | None = Header(None)):
    account = get_account(authorization)
    rows = db.execute(
        "SELECT id, section_number, title FROM sections WHERE course_id = ? ORDER BY display_order",
        (course_id,)
    ).fetchall()

    sections = []
    for sid, num, title in rows:
        status = "not_started"
        if account and account["account_type"] == "user":
            prog = db.execute(
                "SELECT status FROM section_progress WHERE user_id = ? AND section_id = ?",
                (account["id"], sid)
            ).fetchone()
            if prog:
                status = prog[0]
        sections.append({"id": sid, "section_number": num, "title": title, "status": status})

    return {"sections": sections}

@app.get("/api/sections/{section_id}")
def get_section(section_id: int, authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "user":
        return {"error": "Not authenticated"}

    row = db.execute("SELECT id, course_id, section_number, title, content FROM sections WHERE id = ?", (section_id,)).fetchone()
    if row is None:
        return {"error": "Section not found"}

    conversation = get_conversation(account["id"], section_id)

    existing = db.execute(
        "SELECT status FROM section_progress WHERE user_id = ? AND section_id = ?",
        (account["id"], section_id)
    ).fetchone()
    if existing is None:
        db.execute(
            "INSERT INTO section_progress (user_id, section_id, status, started_at) VALUES (?, ?, 'in_progress', ?)",
            (account["id"], section_id, datetime.now(timezone.utc).isoformat())
        )
        db.commit()

    return {
        "section": {"id": row[0], "course_id": row[1], "section_number": row[2], "title": row[3], "content": row[4]},
        "conversation": conversation
    }
@app.post("/api/chat")
def chat(req: ChatRequest, authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "user":
        return {"error": "Not authenticated"}

    row = db.execute("SELECT content FROM sections WHERE id = ?", (req.section_id,)).fetchone()
    if row is None:
        return {"error": "Section not found"}
    section_content = row[0]

    conversation = get_conversation(account["id"], req.section_id)
    save_message(account["id"], req.section_id, "user", req.message)
    conversation.append({"role": "user", "content": req.message})

    reply = teaching_service.generate_teaching_reply(section_content, conversation)
    save_message(account["id"], req.section_id, "assistant", reply)

    return {"reply": reply}

@app.post("/api/sections/complete")
def complete_section(req: CompleteSectionRequest, authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "user":
        return {"error": "Not authenticated"}

    section_row = db.execute("SELECT content, course_id FROM sections WHERE id = ?", (req.section_id,)).fetchone()
    if section_row is None:
        return {"error": "Section not found"}
    section_content, course_id = section_row

    conversation = get_conversation(account["id"], req.section_id)
    if len(conversation) == 0:
        return {"error": "No conversation to evaluate"}

    evaluation = teaching_service.evaluate_section(section_content, conversation)

    db.execute(
        """UPDATE section_progress SET status = 'completed', speed_score = ?, explanation_score = ?,
           question_sharpness_score = ?, evidence = ?, completed_at = ?
           WHERE user_id = ? AND section_id = ?""",
        (evaluation.get("speed_score"), evaluation.get("explanation_score"),
         evaluation.get("question_sharpness_score"), evaluation.get("evidence"),
         datetime.now(timezone.utc).isoformat(), account["id"], req.section_id)
    )
    db.commit()

    total_sections = db.execute("SELECT COUNT(*) FROM sections WHERE course_id = ?", (course_id,)).fetchone()[0]
    completed_sections = db.execute(
        """SELECT COUNT(*) FROM section_progress sp JOIN sections s ON sp.section_id = s.id
           WHERE sp.user_id = ? AND s.course_id = ? AND sp.status = 'completed'""",
        (account["id"], course_id)
    ).fetchone()[0]

    credential_issued = False
    if completed_sections >= total_sections:
        existing_cred = db.execute(
            "SELECT id FROM credentials WHERE user_id = ? AND course_id = ?", (account["id"], course_id)
        ).fetchone()
        if existing_cred is None:
            db.execute(
                "INSERT INTO credentials (user_id, course_id, issued_at) VALUES (?, ?, ?)",
                (account["id"], course_id, datetime.now(timezone.utc).isoformat())
            )
            db.commit()
            credential_issued = True

    return {"completed": True, "credential_issued": credential_issued}

@app.get("/api/my/credentials")
def my_credentials(authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "user":
        return {"error": "Not authenticated"}

    rows = db.execute(
        """SELECT c.title, cr.issued_at FROM credentials cr JOIN courses c ON cr.course_id = c.id
           WHERE cr.user_id = ?""",
        (account["id"],)
    ).fetchall()
    return {"credentials": [{"course_title": r[0], "issued_at": r[1]} for r in rows]}

@app.get("/api/employer/candidates")
def list_candidates(authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "employer":
        return {"error": "Not authenticated"}

    users = db.execute("SELECT id, name, email, current_company FROM users").fetchall()
    result = []
    for uid, name, email, company in users:
        creds = db.execute(
            """SELECT c.title, cr.issued_at FROM credentials cr JOIN courses c ON cr.course_id = c.id
               WHERE cr.user_id = ?""", (uid,)
        ).fetchall()
        scores = db.execute(
            """SELECT s.title, sp.speed_score, sp.explanation_score, sp.question_sharpness_score, sp.evidence
               FROM section_progress sp JOIN sections s ON sp.section_id = s.id
               WHERE sp.user_id = ? AND sp.status = 'completed'""", (uid,)
        ).fetchall()
        result.append({
            "id": uid, "name": name, "email": email, "current_company": company,
            "credentials": [{"course_title": c[0], "issued_at": c[1]} for c in creds],
            "section_scores": [{"section_title": s[0], "speed": s[1], "explanation": s[2], "sharpness": s[3], "evidence": s[4]} for s in scores]
        })
    return {"candidates": result}

@app.post("/api/employer/jobs")
def create_job(req: JobPostingRequest, authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "employer":
        return {"error": "Not authenticated"}

    db.execute(
        "INSERT INTO job_postings (employer_id, title, description, required_course_ids, created_at) VALUES (?, ?, ?, ?, ?)",
        (account["id"], req.title, req.description, json.dumps(req.required_course_ids), datetime.now(timezone.utc).isoformat())
    )
    db.commit()
    return {"success": True}

@app.get("/api/employer/jobs")
def list_jobs(authorization: str | None = Header(None)):
    account = get_account(authorization)
    if account is None or account["account_type"] != "employer":
        return {"error": "Not authenticated"}

    rows = db.execute(
        "SELECT id, title, description, required_course_ids FROM job_postings WHERE employer_id = ?",
        (account["id"],)
    ).fetchall()

    jobs = []
    for jid, title, desc, req_courses_json in rows:
        required_course_ids = json.loads(req_courses_json)
        matched = db.execute(
            f"""SELECT DISTINCT u.id, u.name, u.email FROM users u
                WHERE (SELECT COUNT(DISTINCT course_id) FROM credentials WHERE user_id = u.id AND course_id IN ({','.join('?'*len(required_course_ids))})) = ?""",
            (*required_course_ids, len(required_course_ids))
        ).fetchall() if required_course_ids else []
        jobs.append({
            "id": jid, "title": title, "description": desc,
            "matched_candidates": [{"id": m[0], "name": m[1], "email": m[2]} for m in matched]
        })

    return {"jobs": jobs}

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="static", html=True), name="static")
