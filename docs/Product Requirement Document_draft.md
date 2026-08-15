# Talent Bridge — Product Requirements Document

## Definitions

- **MC (Micro-credential)** — the atomic unit of a course. One MC maps to one concept/skill and carries a depth score, an exercise/scenario history, and a competency summary.
- **Section** — a sequential sub-unit of a course (e.g., 1.1, 1.2, 1.3). A learner must demonstrate understanding of a section via a conversation with the AI instructor before unlocking the next one.
- **Depth score** — a 0–10 AI-assigned score representing how well a user understands a concept. 10 = fully familiar. Currently defined as derived from three evaluated dimensions of a section conversation: speed to real understanding, quality of the learner's own explanation, and sharpness of the learner's questions. *(The exact formula combining the three dimensions into one 0–10 number is not yet defined — see [Open Questions](#5-open-questions).)*
- **Competency decay** — the automatic reduction of a depth score over time when a user is unemployed, modeling skill atrophy.
- **Evidence log** — the record of quoted excerpts from a learner's actual conversation that justifies a given evaluation, as opposed to an opaque numeric score.
- **Sandbox exercise** — a cloud workspace simulating a real data-center incident (e.g., storage array failure, latency spike) that a learner must troubleshoot.
- **PDPA** — Indonesia's Personal Data Protection Law (UU PDP). Referenced here regarding what recruiter-facing skill data is and isn't exposed.
- **MVP** — the hackathon-scope build described in `slide_summary.md`: FastAPI + Claude (via OpenRouter) + SQLite + static HTML/JS on a single self-managed Linux server.
- **OpenRouter** — a unified, OpenAI-compatible API gateway that routes model calls to Claude (and other providers) behind a single API. Used instead of calling Anthropic's API directly so the model provider is a config value, not a hardcoded SDK dependency.

## 1. Problem and User

Batam's unemployment sits in the wrong half of the labour market for what's being built. Its open unemployment rate was 7.68% in 2024 — 50,431 people — more than half of them SMA graduates, followed by SMK graduates, and only 13.74% of Batam's workers hold tertiary qualifications against 35.38% with SMA and 22.94% with SMK. Meanwhile the investment arriving is capital-intensive: a 50 MW data center employs 1,500–2,000 workers during construction but only 50–150 once operational, versus 8,000–12,000 direct jobs for equivalent manufacturing investment. So Rp120 trillion of digital investment produces a permanent headcount too small, and too specialised, to touch the group that is actually unemployed. ([source](https://gokepri.com/mengapa-investasi-besar-belum-mengurangi-pengangguran-di-batam/))
([source](https://kepri.antaranews.com/berita/187707/tingkat-pengangguran-terbuka-di-batam-turun-142-persen))
([source](https://metropolis.batampos.co.id/data-center-padat-modal-serapan-tenaga-kerja-tidak-besar/))

**Who hurts:**

- **Batam's unemployed/underemployed workforce** — largely SMA/SMK graduates who need a fast path into data-center-adjacent technical roles, but lack access to specialized, job-relevant training.
- **Employers in Batam and Singapore** hiring for these roles, who cannot tell from a resume or a completion certificate whether a candidate actually understands the material.

**Current workaround:** workers self-teach via YouTube, Udemy, Coursera, or Pluralsight — platforms with genuinely good expert content — then walk away with a multiple-choice quiz result and a "Certificate of Completion." That certificate proves the video was watched, not that the material was understood. Employers, lacking a better signal, fall back on resume claims, interviews, or the prestige of the issuing platform — none of which measure competency directly.

**Why now:** the mismatch is happening today — capital is arriving faster than the workforce can be made legible to it. Closing the gap requires a fast, trustworthy way to build exactly the skills these roles need and prove them credibly, rather than waiting for a generational shift in tertiary education attainment.

## 2. Goals and Non-Goals

**Goals**

1. Fill the knowledge gaps of our users and validate their competency by demonstrated understanding, not prestige of the issuing platform.
2. Design courses tightly scoped to real job requirements — "down to the T" — rather than generic curricula.
3. Give recruiters an objective, evidence-backed way to assess a candidate's competency in a specific skill, not merely whether they hold a credential.

**Non-goals**

- Not a general-content MOOC platform competing with Udemy/Coursera/Pluralsight on catalog breadth — those platforms' content is not the problem being solved; what happens *after* the content is.
- Not a black-box AI ranking or relevance-scoring system for employers. Matching is built on verified, completed prerequisites only — an employer sees "who genuinely earned this credential," not an opaque score.
- Not a fully autonomous AI content pipeline. AI drafts course content, but every course is reviewed and validated by a human domain expert before it reaches a learner.
- Not (for MVP) a horizontally-scaled, multi-service infrastructure. The MVP is a single self-managed Linux server with SQLite; distributed infra (K8s, load-balanced services) is out of scope until real usage requires it.
- Not (for MVP) a fully-realized data-center sandbox. Solution 3 (incident simulation) is exploratory — see [Scope Boundaries](#3-scope-boundaries-mvp-vs-future) and [Open Questions](#5-open-questions).
- Not scoped narrowly to Batam. The core mechanism — course → AI-gated sections → evidence-based credential — must generalize to other fields/regions; Batam's data-center boom is the launch vertical, not a hard boundary.

## 3. Scope Boundaries (MVP vs. Future)

Grounded in the current repo state (`main.py`, `schema.sql`, `services/`), not just stated intent — "in scope" and "built" are not the same thing yet.

**Implemented today:**

- Learner + employer auth — separate `users`/`employers` tables, bearer tokens via `auth_tokens` ([services/auth_service.py](services/auth_service.py)).
- Course/section browsing, Socratic chat per section, three-dimension evaluation, credential issuance once every section in a course is completed ([services/teaching_service.py](services/teaching_service.py), `main.py` `/api/chat` and `/api/sections/complete`).
- Employer job postings with exact-match candidate matching against issued credentials (`main.py` `/api/employer/*`).
- Static HTML/CSS/JS frontend served by the same FastAPI process.

**Stated as a decision but not yet enforced in code — a real gap, not an intentional non-goal:**

- Section gating ([Decision 4](#4-decisions-already-made)) — the schema and API track per-section status, but `GET /api/sections/{id}` and `POST /api/chat` do not currently check that prior sections are completed before serving content. See [Sequencing](#12-sequencing) item 5 and [Verification Loop](#13-verification-loop).
- Human review gate ([Decision 5](#4-decisions-already-made)) — the `courses` table has no review/approval/status column; review currently happens out-of-band (manual check before content is seeded), not as a recorded, checkable gate.

**Not started / out of MVP scope:**

- MC as a first-class entity with a `depth_score` and competency decay (Solution 1) — today, evaluation scores live per-section (`section_progress.speed_score` etc.), not aggregated per concept/skill with decay applied.
- Sandbox scenario simulation (Solution 3) — see the companion doc [Sandbox_Architecture.md](Sandbox_Architecture.md) for the proposed (not yet built) architecture.
- Live LinkedIn job scraping — `generate_courses.py` seeds a fixed list of 3 hardcoded course topics, not a per-user job-description input.
- Horizontal scaling / distributed infrastructure — single SQLite file, single process today. A microservices split (`services/*/worker.py`, `common/rpc.py` Redis-backed RPC, `gateway/`) is in progress but not wired into `main.py` yet — the live app still imports `auth_service`/`teaching_service` as local modules, not over the queue. Formal legal PDPA sign-off on recruiter-visible data also remains outstanding (currently an internal assumption, not a verified conclusion).

## 4. Decisions Already Made

Each decision below is settled; the rationale tells you whether it's load-bearing (don't casually change it) or a judgment call (fine to revisit if a better option surfaces).

1. **Bottom-up competency signal, not top-down course completion.** *Why:* Coursera-style platforms tell you a learner covered a skill, not how well — recruiters are left guessing which "skills" on a profile are noise. Talent Bridge instead reports a level of competency per skill. Load-bearing — this is the product's core differentiator.
2. **Full transparency down to exercise/evaluation evidence, no black-box scores.** *Why:* an employer or learner can independently check *why* a score is what it is (a quoted excerpt from the actual conversation), rather than trusting an opaque number. This is also the answer to the "isn't scoring learners a privacy concern?" objection — the learner knows upfront it's happening. Load-bearing.
3. **Competency decay: −0.5 per 3 months while unemployed, off a 0–10 scale, bottoming out at 2.5 years.** *Why:* models real skill atrophy so a credential earned years ago doesn't read as current. Score refreshes on newer completed exercises. Skills tied to a role the user is currently employed in do **not** decay. Load-bearing for the "no PDPA concerns" and "credentials stay honest" claims.
4. **Courses are broken into sequential, gated sections (1.1, 1.2, 1.3, …); a learner cannot skip ahead.** *Why:* progressing requires a real conversation with the AI instructor where the learner explains the concept back in their own words — this is the mechanism that turns "watched the video" into "demonstrated understanding." Load-bearing.
5. **AI drafts course content; a human domain expert reviews and validates every course before it reaches a learner.** *Why:* AI-assisted authoring without blind trust in AI output — addresses the "how do you know the content is accurate" objection directly. Load-bearing; do not remove the human-review gate to "move faster."
6. **Direct model calls to Claude via OpenRouter, rather than a heavier agent framework.** *Why:* precise control over the teaching and evaluation prompts without unnecessary complexity, and routing through OpenRouter (rather than Anthropic's API directly) keeps the model provider a config value instead of a hardcoded SDK dependency — swapping models or providers later doesn't require rewriting the call sites. Judgment call — revisit if orchestration needs (e.g., Solution 2's persistent memory across notes/chats) outgrow hand-rolled prompt management.
7. **Matching is built on verified completed prerequisites, not a ranking algorithm.** *Why:* an employer lists required course credentials; the system returns every candidate who genuinely earned them. No black box to defend. Load-bearing.
8. **MVP tech stack: Python + FastAPI, Claude via OpenRouter, SQLite, static HTML/CSS/JS, single self-managed Linux server (systemd-managed, auto-restart).** *Why:* fast to build, nothing to break live during a demo, and the real cost/scaling driver is AI API usage (which scales with actual usage) rather than fixed infrastructure. Judgment call for MVP; revisit before any real multi-tenant launch.
9. **Recruiter-facing tracing shows skill/exercise history and summaries only.** *Why:* stated rationale is that this avoids PDPA concerns since it's competency evidence, not personal data. Treated as a working assumption — see [Open Questions](#5-open-questions) for the unresolved legal-verification gap.

## 5. Open Questions

| Question | What to do about it |
| :---- | :---- |
| How do we realistically simulate data-center infrastructure failures (storage array down, latency spikes, connectivity loss) for Solution 3? Which components need to be mocked, and how is a per-scenario configuration authored? | Do not commit engineering time to K8s/Terraform sandbox build-out until a small spike proves at least one failure scenario can be mocked convincingly. Treat Solution 3 as exploratory/post-MVP until then. |
| What is the exact formula that combines the three evaluated dimensions (speed, explanation quality, question sharpness) into the single 0–10 depth score? | Needs to be specified before depth score can be implemented consistently. Flag to product/eng owner; don't guess a weighting without sign-off. |
| Is the "no PDPA concerns" claim for recruiter-visible skill tracing actually correct under Indonesian law, or is it an untested assumption? | Get a legal read before recruiter-facing tracing ships broadly. Until confirmed, treat as an assumption, not a decision. |
| What does the human-review/appeal path for disputed AI evaluations look like? (Slide summary notes: "a production version would add" this — it doesn't exist yet.) | Out of MVP scope; design when evaluation disputes become a real, observed problem rather than speculatively now. |
| How will live LinkedIn job scraping actually work (rate limits, ToS, data freshness) once we move past the MVP's hand-picked sample job description? | Out of MVP scope. Revisit only once Solution 2 needs a live job feed instead of a fixture. |

## 6. Features

### Solution 1: Micro-credentials (MCs)

- Core unit of each designed course.
- Data format:
  - **Concept**
    - Depth score, assigned by AI (see [Definitions](#definitions) for how it's currently derived).
    - Exercise + scenario history backing the score (resource link to a table with supporting UI).
    - Summary of the user's skill competency (resource link to a subtab under the user's profile).
- Recruiters can see tracing history for a skill's competence, based on the summary and exercise history — not on raw personal data (see [Open Questions](#5-open-questions) on PDPA verification).
- **Competency Decay** (see [Decision 3](#4-decisions-already-made)): −0.5 every 3 months while unemployed, off a 10-point scale, bottoming out at 2.5 years; refreshed by newer completed exercises; frozen (no decay) while employed in a role that uses the skill.
- **Differentiating factors from current solutions:**
  - Coursera's model is top-down — it surfaces which courses cover relevant skills, but that doesn't tell a recruiter whether the "skills" listed are noise. Talent Bridge is bottom-up: it reports a *level of competency* per skill, not a binary "has the skill or not."
  - Where Coursera's outcomes are vague or its assessments disconnected from the material, a learner can't articulate what they can now do that they couldn't before — and there's nowhere for a recruiter to check. MCs are transparent end-to-end, down to the exercise/evidence history.

### Solution 2: Micro-credential-centered Course Creation and Management

- Course creation is anchored to real jobs scraped from LinkedIn — both existing and new data-center roles. **For the MVP, this uses a sample job description instead of a live scrape** (see [Scope Boundaries](#3-scope-boundaries-mvp-vs-future)).
- Users submit or select a job description; an AI-orchestration system designs the course based on that job and the user's current competencies.
- Courses are broken into sequential, gated sections (1.1, 1.2, 1.3, …). A learner cannot skip ahead — advancing requires a real conversation with the AI instructor where the learner explains the concept back in their own words and demonstrates genuine understanding, not just click-through completion.
- While that conversation happens, the system transparently evaluates three things: how quickly the learner reached real understanding, how well they explained it back, and how sharp their own questions were. The learner knows this evaluation is happening — it is not hidden.
- A credential (MC) is issued only once every section of a course is genuinely completed.
- Users can write notes and chat about blockers or new concepts; this is ingested by AI and documented via persistent memory.
- Summary pointers let the user review their own performance, and let recruiters see whether the user is a good fit and on-track with a job's requirements — giving both the company and the user visibility into progress.
- **AI drafts course content; a human domain expert reviews and validates every course for technical accuracy before it reaches a learner** (see [Decision 5](#4-decisions-already-made)).

### Solution 3: Sandbox-based Scenario Setup for Incident Simulation *(exploratory — see [Open Questions](#5-open-questions))*

- Users select incident exercises modeled on real data-center scenarios — e.g., a server becoming unavailable, or an application facing unprecedented latency.
- Users access a cloud workspace via a resource-link URL; this workspace is a sandbox mocking data-center functions/components, aiming to mimic the scenario as realistically as possible.
- Exercises are designed via configuration files; cloud workspaces are issued through K8s; configuration is set up via Terraform, specifically to trigger an incident.
- Users troubleshoot the sandbox to restore functionality, then run a test suite to confirm the exercise is complete.
- **Unresolved:** which components need to be mocked and how, for the simulation to be realistic and buildable — this is not yet solved and should not be treated as MVP-committed work.

## 7. Interfaces and Data Contracts

These are proposed shapes to align frontend, backend, and AI-orchestration work — not yet implemented as such. Treat field names as provisional; the contract (what data must exist and who reads/writes it) is the part that matters. `schema.sql` is the current ground truth and differs from this in places (integer auto-increment IDs, no `concept_id`/`depth_score` columns yet — see [Scope Boundaries](#3-scope-boundaries-mvp-vs-future)).

### MC (Micro-credential) record

```text
MC {
  concept_id: string
  concept_name: string
  depth_score: float            // 0.0–10.0
  last_scored_at: date
  is_decay_frozen: boolean      // true if tied to a role the user is currently employed in
  exercise_history: [ExerciseResult]   // ordered, most recent last
  summary: string               // shown under user profile subtab
}

ExerciseResult {
  exercise_id: string
  section_id: string            // e.g. "1.2"
  evidence_quotes: [string]     // excerpts from the learner's conversation backing the score
  dimension_scores: {
    speed_to_understanding: float
    explanation_quality: float
    question_sharpness: float
  }
  completed_at: datetime
}
```

### Course / Section

```text
Course {
  course_id: string
  source_job_description_id: string   // sample fixture in MVP; live LinkedIn posting later
  sections: [Section]                 // ordered: 1.1, 1.2, 1.3, ...
}

Section {
  section_id: string        // e.g. "1.2"
  concept_id: string         // -> MC.concept_id
  unlocked_after: string | null   // section_id of prerequisite, null for 1.1
  completion_requires: "ai_gated_conversation"
}
```

### Employer matching request/response

```text
JobRequirement {
  job_id: string
  required_course_ids: [string]
}

MatchResult {
  candidate_id: string
  matched: boolean            // true only if all required courses are fully, genuinely completed
  mc_summaries: [MC.summary]  // linked evidence, not a black-box score
}
```

## 8. Acceptance Criteria

- **MC depth score:** given a completed exercise with `dimension_scores` for speed/explanation/question-sharpness, the system computes and stores a `depth_score` between 0.0 and 10.0, with at least one `evidence_quotes` entry attached.
- **Decay:** an MC belonging to an unemployed user, unscored for 3 full months, has its `depth_score` reduced by exactly 0.5 (floored at 0.0) at the next evaluation cycle; an MC tied to a role the user is currently employed in shows `is_decay_frozen = true` and its score is unchanged across the same period.
- **Section gating:** a learner cannot access `section 1.2` content until `section 1.1` is marked complete via an AI-gated conversation; attempting to access it directly is rejected. *(Not yet true of the current implementation — see [Scope Boundaries](#3-scope-boundaries-mvp-vs-future).)*
- **Credential issuance:** an MC/credential is only marked issued when every section in its course has `completion_requires` satisfied — partial completion never issues a credential.
- **Human review gate:** an AI-drafted course cannot reach `published` status without a recorded human-reviewer approval on the course record. *(No `published`/review column exists in `courses` yet — this is a target, not current behavior. See [Scope Boundaries](#3-scope-boundaries-mvp-vs-future).)*
- **Recruiter visibility:** a recruiter viewing a candidate's MC sees `exercise_history` and `summary` fields only — no raw personal data beyond what's needed to identify the candidate.
- **Matching:** given a `JobRequirement.required_course_ids`, `MatchResult.matched` is `true` for a candidate if and only if every required course is fully completed (all sections, all credentials issued) — never a partial or fuzzy match.

## 9. Worked Examples

**Decay — normal case:** A user has a "Storage Array Troubleshooting" MC at depth score 8.0, then becomes unemployed. After 3 months with no new exercises, the score drops to 7.5. After 6 months, 7.0. If they complete a new relevant exercise scoring an equivalent of 9.0 at month 4, the stored score refreshes upward to reflect that newer performance rather than continuing to decay from 7.5.

**Decay — edge case (employed, skill protected):** A user holds the same MC at 8.0 and is currently employed in a role that uses "Storage Array Troubleshooting." No decay is applied at month 3, 6, or any point while that employment continues, regardless of whether they complete new exercises.

**Decay — failure/boundary case:** A user's MC starts at 2.0 and stays unemployed with no new exercises. After 12 months, standard decay (4 × −0.5) would produce 0.0. The score floors at 0.0 rather than going negative; it does not disappear from the profile — it remains visible as evidence the skill was once demonstrated.

**Section gating:** A learner finishes reading section 1.1 ("What is a storage array?"). To unlock 1.2, they must have a conversation with the AI instructor, explain in their own words what a storage array is and why redundancy matters, and answer a follow-up probing question. If they can only repeat memorized phrases without engaging with the follow-up, the section stays locked and the AI flags the specific gap for another attempt.

**Employer matching:** An employer posts a "Data Center Operations Technician" role requiring `["storage-fundamentals-101", "network-troubleshooting-201"]`. Candidate A completed both courses (all sections, credentials issued) — `matched: true`, and the employer sees A's linked exercise history and summaries. Candidate B completed `storage-fundamentals-101` but only sections 2.1–2.2 of `network-troubleshooting-201` — `matched: false`; B does not appear in the results, regardless of how strong B's resume looks.

## 10. Constraints

- **MVP tech stack is fixed** per [Decision 8](#4-decisions-already-made): Python + FastAPI backend, Claude via OpenRouter for teaching/evaluation/content-drafting, SQLite, static HTML/CSS/JS frontend, single self-managed Linux server with systemd. Do not introduce a framework, database server, or build pipeline "for scale" until real usage demands it.
- **No AI-drafted course content ships without human expert review** ([Decision 5](#4-decisions-already-made)) — this gate cannot be bypassed for speed.
- **No opaque scoring.** Every evaluation surfaced to a learner or recruiter must trace back to quoted evidence from the actual conversation — this is both a trust mechanism and the current answer to privacy objections ([Decision 2](#4-decisions-already-made)).
- **Matching must remain rule-based on verified prerequisites**, not a ranking/relevance model — this is explicitly called out in the prepared Q&A as a differentiator, not an implementation detail to optimize away.
- **PDPA exposure is an unverified assumption, not a cleared constraint** — see [Open Questions](#5-open-questions). Do not expand recruiter-visible data fields without re-checking this.
- **Solution 3 has no committed technical approach.** K8s/Terraform is the current best guess for the sandbox, but the harder problem (what to mock, how to make it realistic) is unsolved — don't treat the infra choice as validating the feature's feasibility.

## 11. Escalation Rules

When to stop and get a decision from the product owner rather than assuming an answer:

- If a scoring or decay formula changes in a way that would retroactively alter already-issued credentials — stop. Issued credentials are the trust artifact this product sells; silently reshaping their meaning after the fact undermines the core pitch.
- If the PDPA legal review ([Open Questions](#5-open-questions)) comes back negative — stop expanding recruiter-facing tracing fields immediately and roll back to the minimum needed, rather than continuing to build on an unconfirmed assumption.
- If the Solution 3 mock-fidelity spike ([Sandbox_Architecture.md §9](Sandbox_Architecture.md#9-open-questions)) shows a scenario can't be simulated convincingly in the available time — stop and flag it; cut the feature from the pitch rather than demoing something unconvincing.
- If a human course reviewer rejects or substantially rewrites an AI-drafted course more than occasionally — stop and flag it to the product owner. That's a signal the drafting prompt needs redesign, not something to quietly patch course-by-course.
- Before implementing section-gating enforcement (currently missing — see [Scope Boundaries](#3-scope-boundaries-mvp-vs-future)) — stop and confirm the exact prerequisite rule. "Cannot skip ahead" doesn't say whether *all* prior sections must be complete or just the immediately preceding one; don't guess the semantics and wire up auth checks against it.
- Do not silently drop a load-bearing decision from [section 4](#4-decisions-already-made) to hit a deadline. If it can't be met in time, that's an escalation, not a scope call to make unilaterally.

## 12. Sequencing

Build order matters because several pieces have hard dependencies, and because the demo's highest-leverage moment — a live conversation catching a misconception — doesn't require every feature to exist.

1. Auth + course/section schema — **done** (`users`, `employers`, `courses`, `sections`, `auth_tokens`).
2. Socratic teaching loop + evaluation (`teaching_service.py`, `/api/chat`, `/api/sections/complete`) — **done**. This is the single most convincing demo moment; prioritize polishing this over anything below it.
3. Credential issuance on full-course completion — **done**, depends on (2).
4. Employer job posting + exact-match candidate matching — **done**, depends on (3) needing credentials to match against.
5. Section-gating enforcement at the API level — **not done**; no new dependency, but must be resolved before [Decision 4](#4-decisions-already-made) ("cannot skip ahead") is true end-to-end rather than just an authoring intent.
6. MC entity with `depth_score` + competency decay (Solution 1) — **not started**; depends on (2)'s evaluation output being reshaped into a per-concept score rather than per-section, so resolve whether "concept" maps 1:1 to "section" or spans several before building this.
7. Sandbox (Solution 3) — **not started**, exploratory. Do not sequence this before (5) and (6) — it's the least-validated of the three solutions and shouldn't compete with core-loop polish for time.
8. Microservices split (`gateway/`, Redis RPC via `common/rpc.py`, `services/*/worker.py`) — **in progress**, not wired into `main.py` yet. Treat as infrastructure hardening that can happen any time after (2)–(4) are stable — it changes deployment shape, not product behavior.

## 13. Verification Loop

How to confirm each piece is actually done and correct, not just "looked fine in a quick click-through." No automated test suite exists yet — everything below is currently manual (curl/Postman + reading the SQLite file directly).

- **Auth:** `POST /api/auth/signup/user` → `/api/auth/login/user` → `GET /api/auth/me` with the returned bearer token; confirm the account round-trips. Repeat for the `/employer` variants.
- **Teaching loop:** `POST /api/chat` on a fresh section; confirm the reply stays scoped to that section's content (manual check — no automated topic-scoping check exists).
- **Evaluation + credential issuance:** complete every section of a course via `/api/sections/complete`, then check `GET /api/my/credentials` lists it. Also verify re-completing an already-completed section doesn't duplicate the credential row (issuance is guarded by an `existing_cred is None` check in `main.py`, but confirm this manually after a retry).
- **Section gating:** attempt `GET /api/sections/{id}` for a later section before completing an earlier one. As of this writing this succeeds (no rejection) — this check will fail until the [Sequencing](#12-sequencing) item 5 gap is closed, and that's expected until then, not a false alarm.
- **Matching:** create a job posting with `required_course_ids`, issue credentials to a candidate for a subset vs. all of them, and confirm `GET /api/employer/jobs` includes that candidate in `matched_candidates` only once every required course is present.
- The highest-value first automated tests to add would cover credential issuance and matching, since "verified prerequisites, not a black box" is the specific claim the pitch's credibility rests on.

## 14. Demo Checklist

- Run a live conversation in the demo that catches a real misconception — showing this beats describing it.
- Confirm the "completion vs. understanding" framing lands early and isn't buried under the market-data setup.
- Be ready to say "I reviewed and validated the content" plainly — it's a genuine strength, not a caveat to soften.
- For any question without a clean answer (e.g., Solution 3 feasibility, PDPA verification), the prepared response is: "That's a great question — for this MVP, here's the honest current state..." rather than overselling a resolved answer.
- Before calling any feature "done," check it against both the [Acceptance Criteria](#8-acceptance-criteria) and the [Verification Loop](#13-verification-loop) above — not just "the demo looked fine."
