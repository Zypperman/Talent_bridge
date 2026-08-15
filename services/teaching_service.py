"""
Talent Bridge Teaching Service — runs a Socratic conversation scoped to
ONE section's content, then evaluates the learner's understanding across
three parameters: speed, explanation quality, question sharpness.
"""

import os, json, sqlite3
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
_DB_PATH = "/opt/talentbridge/data/talentbridge.db"


def _get_db():
    return sqlite3.connect(_DB_PATH, check_same_thread=False)


TEACHING_SYSTEM_PROMPT = """You are a technical instructor for a data-center operations training platform. You are teaching ONE specific section of a course, described below. Stay strictly within the scope of this section's content — do not wander into other topics.

Follow a Socratic approach: ask diagnostic questions, let the learner explain concepts in their own words, correct misconceptions gently, and confirm real understanding before considering the section complete. Do not just lecture — genuinely check the learner's grasp of the material through questions.

SECTION CONTENT TO TEACH:
{section_content}

Keep each response focused on one idea at a time. When you believe the learner has demonstrated genuine understanding of this section's core idea, say so clearly and let them know they can mark it complete."""


def generate_teaching_reply(section_content, conversation):
    system_prompt = TEACHING_SYSTEM_PROMPT.format(section_content=section_content)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system_prompt,
        messages=conversation
    )
    return response.content[0].text


EVALUATION_PROMPT = """Below is a full conversation transcript between a learner and an AI instructor covering one training section. Evaluate the learner's performance across exactly three parameters.

SECTION CONTENT:
{section_content}

TRANSCRIPT:
{transcript}

Respond with ONLY valid JSON, no markdown fences, no other text, in this exact format:

{{
  "speed_score": 0.0,
  "explanation_score": 0.0,
  "question_sharpness_score": 0.0,
  "evidence": "one or two sentences citing specific things the learner said or asked that justify these scores"
}}

Scoring guide, each from 0.0 to 1.0:
- speed_score: how efficiently the learner reached genuine understanding (fewer clarifying loops needed = higher score). Do not reward speed if understanding was shallow.
- explanation_score: how well the learner explained concepts back in their own words, based on evidence in the transcript, not assumption.
- question_sharpness_score: the depth and insight of questions the learner asked, if any. Surface-level or no real questions = low score. Genuinely probing, specific questions = high score.

Be honest and evidence-based. Do not give high scores without clear evidence in the transcript."""


def evaluate_section(section_content, conversation):
    transcript = ""
    for msg in conversation:
        transcript += f"{msg['role'].upper()}: {msg['content']}\n\n"

    prompt = EVALUATION_PROMPT.format(section_content=section_content, transcript=transcript)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"speed_score": None, "explanation_score": None, "question_sharpness_score": None, "evidence": "Evaluation failed to parse"}
