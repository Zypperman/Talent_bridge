# Talent Bridge — Slide Content Plan

Content outline derived from `Product Requirement Document_draft.md`, restructured
slide-by-slide. This is the planning doc; the presentable Marp deck built from it
lives at `slides/slides.md` (run `npm run preview` inside `slides/` to view it).

Each `## Slide N` entry becomes one slide. Lines under `Notes:` are speaker notes,
not on-slide content. Each of the three solutions gets an intro slide in a fixed
three-part format — **problem it addresses → how it solves that problem → what's
different from existing solutions** — followed by whatever mechanics/detail slides
are needed.

---

## Slide 1 — Title

**Talent Bridge**
Proving understanding, not attendance.

Notes: Batam data-center hiring, hackathon pitch context.

## Slide 2 — Hook

"Batam's data-center boom is creating real technical jobs — but most of Batam's
current tech workforce is in operational roles, not the specialized engineering
roles this boom needs. The question is: how do you close that gap fast, and how
does an employer actually trust that someone is ready?"

## Slide 3 — The Problem

- Batam open unemployment: **7.68%** in 2024 — 50,431 people
- Most are SMA/SMK graduates; only **13.74%** of Batam's workforce holds tertiary
  qualifications
- Data centers are capital-intensive, not labour-intensive: a 50MW facility employs
  1,500–2,000 during construction but only **50–150** once operational — vs.
  8,000–12,000 direct jobs for equivalent manufacturing investment
- Rp120 trillion of digital investment → a permanent headcount too small and too
  specialised to touch the people who are actually unemployed

## Slide 4 — Who Hurts

- **Batam's unemployed/underemployed workforce** — need a fast path into
  data-center-adjacent technical roles, but lack access to specialized,
  job-relevant training
- **Employers in Batam and Singapore** — can't tell from a resume or a completion
  certificate whether a candidate actually understands the material

## Slide 5 — Current Workaround Fails

- Workers self-teach via YouTube, Udemy, Coursera, Pluralsight — genuinely good
  expert content
- They walk away with a multiple-choice quiz result and a **"Certificate of
  Completion"**
- **That certificate proves the video was watched — not that the material was
  understood.**
- Employers fall back on resume claims, interviews, or platform prestige — none of
  which measure competency directly

## Slide 6 — Why Now

Capital is arriving faster than the workforce can be made legible to it. Closing
the gap means building exactly the skills these roles need and proving them
credibly — not waiting a generation for tertiary attainment to catch up.

## Slide 7 — The Solution

**Learning through real conversation, not content consumption.**

1. Micro-credentials — competency, scored and evidenced, not a certificate
2. Socratic, section-gated course creation — can't skip ahead, can't fake it
3. (Exploratory) sandbox incident simulation for hands-on practice

## Slide 8 — Goals

1. Fill knowledge gaps and validate competency by demonstrated understanding —
   not the prestige of the issuing platform
2. Design courses tightly scoped to real job requirements, "down to the T"
3. Give recruiters an objective, evidence-backed way to assess a specific skill —
   not just whether a credential exists

## Slide 9 — Non-Goals

- Not a general-content MOOC platform competing on catalog breadth
- Not a black-box AI ranking/relevance system for employers
- Not a fully autonomous AI content pipeline — human expert reviews every course
- Not (for MVP) horizontally-scaled infra, or a fully-realized sandbox
- Not scoped narrowly to Batam — the mechanism must generalize

## Slide 10 — Solution 1: Micro-Credentials

**The problem:** A completion certificate proves a video was watched — not that
the material was understood. Employers can't tell which "skills" on a profile are
real.

**How this solves it:** Every concept becomes a Micro-Credential: an AI-assigned
depth score (0–10) backed by an evidence log of quoted excerpts from the learner's
own conversation — not a pass/fail checkbox.

**What's different:** Coursera-style platforms are top-down — they tell you a
course covered a skill. Talent Bridge is bottom-up — it reports *how well*, and
every score traces back to evidence anyone can check. No black box.

## Slide 11 — Inside a Micro-Credential

- The atomic, scored unit of a course: one concept/skill
- Contains: depth score (0–10), exercise/scenario history, competency summary
- The score updates as new exercises complete — see Competency Decay (Slide 13)

## Slide 12 — Depth Score

AI-assigned, 0–10, derived from three dimensions of a section conversation:

- **Speed** to real understanding
- **Quality** of the learner's own explanation
- **Sharpness** of the learner's follow-up questions

Every score carries an evidence log — quoted excerpts from the actual
conversation, not an opaque number.

*(Open question: the exact formula combining the three dimensions is not yet
defined — see Slide 23.)*

## Slide 13 — Competency Decay

- **−0.5 every 3 months** while unemployed, off a 0–10 scale, floors at 0
- Refreshes upward on newer completed exercises
- **Frozen** while employed in a role that uses the skill — no decay
- Models real skill atrophy so an old credential doesn't read as current

**Example:** MC at 8.0 → unemployed 3 months → 7.5 → 6 months → 7.0. A new
exercise scoring 9.0 at month 4 refreshes the stored score upward instead of
continuing to decay.

## Slide 14 — Solution 2: Course Creation & Section Gating

**The problem:** Generic curricula don't map to what a specific job actually
needs, and click-through completion (watch → quiz → certificate) doesn't test
whether the learner understood anything.

**How this solves it:** AI designs each course directly from a real job
description. Content is split into sequential, gated sections — a learner can't
advance without a real conversation with the AI instructor, explaining the
concept back and proving genuine understanding.

**What's different:** Scoped "down to the T" to one job, not a fixed catalog
course. Progression is gated by demonstrated understanding, not a quiz, and every
AI-drafted course is validated by a human domain expert before it reaches a
learner.

## Slide 15 — How a Course Gets Built

- Course is anchored to a real job description (MVP: a hand-picked sample;
  future: live LinkedIn scrape)
- Sections numbered sequentially (1.1, 1.2, 1.3, …) — each unlocks only after
  the previous is complete
- Credential issues only once **every** section is genuinely completed

## Slide 16 — Section Gating, Worked Example

A learner finishes reading 1.1 ("What is a storage array?"). To unlock 1.2 they
must:

- Explain in their own words what a storage array is and why redundancy matters
- Answer a follow-up probing question

If they can only repeat memorized phrases without engaging the follow-up, the
section stays locked and the AI flags the specific gap for another attempt.

## Slide 17 — Solution 3: Sandbox Incident Simulation *(exploratory)*

**The problem:** Conceptual understanding alone doesn't prove someone can
troubleshoot a real incident under real conditions — and technical interviews or
tests like HackerRank only measure isolated problem-solving under exam pressure,
in one sitting.

**How this solves it:** Learners get a cloud workspace mocking a real
data-center incident (storage array failure, latency spike) and must
troubleshoot it back to working order, verified by an automated test suite.

**What's different:** Measures applied skill on real infrastructure patterns
tied to the job, not a timed abstract puzzle — though this piece is still
exploratory (see Slide 23).

## Slide 18 — Inside the Sandbox

- Cloud workspace via K8s, incident triggered via Terraform configuration
- Learner troubleshoots to restore functionality, then runs a test suite to
  confirm
- **Unresolved:** which components need to be mocked, and how, to be realistic —
  not MVP-committed work

## Slide 19 — Employer Matching

- Employer lists required course credentials for a role
- System returns every candidate who **genuinely earned** them — all sections,
  all credentials issued
- No ranking algorithm, no black box — rule-based on verified prerequisites
- Employer sees linked exercise history and summaries, not raw personal data

**Example:** Role requires `storage-fundamentals-101` +
`network-troubleshooting-201`. Candidate A completed both → matched. Candidate B
completed only sections 2.1–2.2 of the second course → not matched, regardless of
resume strength.

## Slide 20 — MVP Scope Boundaries

| In MVP scope | Out of scope (future) |
|---|---|
| Solution 1 — MCs, depth scoring, decay | Solution 3 full sandbox (K8s + Terraform) |
| Solution 2 — gated course creation | Live LinkedIn scraping pipeline |
| Single-server stack (FastAPI + Claude via OpenRouter + SQLite) | Horizontal scaling / distributed infra |
| Human review of every AI-drafted course | Human appeal workflow for disputed evaluations |
| Recruiter-facing skill tracing | Formal legal PDPA sign-off |

## Slide 21 — Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Python + FastAPI | Fast to build, routes every learner message to Claude and back |
| AI Engine | Claude, via OpenRouter | Socratic teaching, evaluation, course drafting |
| Database | SQLite | One file, no separate server, reliable at this scale |
| Frontend | Plain HTML/CSS/JS | No build tools, nothing to break live in a demo |
| Hosting | Self-managed Linux, systemd | Runs permanently, auto-restarts, independent of any one machine |

Direct model calls to Claude via OpenRouter, not a heavier agent framework —
precise control over teaching/evaluation prompts without unnecessary
complexity, and the model/provider stays a config value instead of a
hardcoded SDK dependency.

## Slide 22 — Key Decisions (Load-Bearing)

- Bottom-up competency signal, not top-down completion
- Full transparency to evidence — no black-box scores
- Competency decay models real atrophy; frozen while employed
- Sequential gated sections — can't skip ahead
- Human expert reviews every AI-drafted course before publish
- Matching is rule-based on verified prerequisites, not a ranking model

## Slide 23 — Open Questions

- What's the exact formula combining speed / explanation quality / question
  sharpness into one 0–10 depth score? *(needs product/eng sign-off)*
- Is the "no PDPA concerns" claim for recruiter-visible tracing actually correct
  under Indonesian law? *(needs legal read before broad rollout)*
- How do we realistically simulate data-center failures for Solution 3, and what
  needs to be mocked?
- What does a human-review/appeal path for disputed AI evaluations look like?
  *(post-MVP)*
- How will live LinkedIn job scraping work — rate limits, ToS, freshness?
  *(post-MVP)*

## Slide 24 — Closing

"This isn't about replacing human trainers. It's about giving Batam's workforce a
fast, honest way to prove they're ready for these new roles — and giving
employers, whether in Batam or across the strait in Singapore, a reason to
actually trust that signal."

---

## Appendix — Q&A Backup

### A1. Isn't scoring learners a privacy concern?

Fully transparent — the learner knows from sign-up that conversations are
evaluated and that evaluation is what employers see. Nothing hidden; that
transparency is itself part of the trust mechanism. (PDPA legal verification is
still an open item — see Slide 23.)

### A2. How would this scale to thousands of users?

Architecture doesn't need to change — every conversation is already an
independent API call, so it scales horizontally. The real cost driver is AI API
usage, which scales with actual usage rather than fixed infrastructure.

### A3. Why not build on an existing platform?

Existing platforms prove content consumption, not understanding — that's exactly
the gap this exists to close. Direct model calls to Claude via OpenRouter (not a
heavier framework) give precise control over teaching/evaluation prompts without
unnecessary complexity at this stage.

### A4. What if the AI evaluation is wrong or unfair?

Every score is backed by a quoted excerpt from what the learner actually said —
evidence-based, not a bare number. A production version would add a human
review/appeal path on top of the same evidence log (not built yet — see Slide 23).
