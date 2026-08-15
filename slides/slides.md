---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Talent Bridge'
style: |
  section {
    font-size: 26px;
  }
  section.lead h1 {
    font-size: 64px;
  }
  section.lead h2 {
    font-size: 30px;
    font-weight: normal;
    color: #555;
  }
  section.lead blockquote {
    font-size: 28px;
    border-left: none;
    font-style: italic;
    color: #333;
  }
  table {
    font-size: 22px;
  }
  footer {
    font-size: 16px;
    color: #999;
  }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Talent Bridge

## Proving understanding, not attendance.

<!--
Batam data-center hiring, hackathon pitch context.
-->

---

<!-- _class: lead -->

> "Batam's data-center boom is creating real technical jobs — but most of
> Batam's current tech workforce is in operational roles, not the specialized
> engineering roles this boom needs. The question is: how do you close that gap
> fast, and how does an employer actually trust that someone is ready?"

---

## The Problem

- Batam open unemployment: **7.68%** in 2024 — 50,431 people
- Most are SMA/SMK graduates; only **13.74%** of the workforce holds tertiary
  qualifications
- Data centers are capital-intensive, not labour-intensive: a 50MW facility
  employs 1,500–2,000 during construction but only **50–150** once operational
  — vs. 8,000–12,000 direct jobs for equivalent manufacturing investment
- Rp120 trillion of digital investment → a permanent headcount too small and
  too specialised to touch the people who are actually unemployed

---

## Who Hurts

- **Batam's unemployed / underemployed workforce**
  Need a fast path into data-center-adjacent technical roles, but lack access
  to specialized, job-relevant training

- **Employers in Batam and Singapore**
  Can't tell from a resume or a completion certificate whether a candidate
  actually understands the material

---

## The Current Workaround Fails

- Workers self-teach via YouTube, Udemy, Coursera, Pluralsight — genuinely
  good expert content
- They walk away with a multiple-choice quiz result and a **"Certificate of
  Completion"**

> That certificate proves the video was watched — not that the material was
> understood.

- Employers fall back on resume claims, interviews, or platform prestige —
  none of which measure competency directly

---

## Why Now

Capital is arriving faster than the workforce can be made legible to it.

Closing the gap means building exactly the skills these roles need and
proving them credibly — not waiting a generation for tertiary attainment to
catch up.

---

<!-- _class: lead -->

# The Solution

## Learning through real conversation, not content consumption.

1. Micro-credentials — competency, scored and evidenced
2. Socratic, section-gated course creation
3. *(exploratory)* Sandbox incident simulation

---

## Goals

1. Fill knowledge gaps and validate competency by demonstrated
   understanding — not the prestige of the issuing platform
2. Design courses tightly scoped to real job requirements, "down to the T"
3. Give recruiters an objective, evidence-backed way to assess a specific
   skill — not just whether a credential exists

---

## Non-Goals

- Not a general-content MOOC platform competing on catalog breadth
- Not a black-box AI ranking / relevance system for employers
- Not a fully autonomous AI content pipeline — human expert reviews every
  course
- Not (for MVP) horizontally-scaled infra, or a fully-realized sandbox
- Not scoped narrowly to Batam — the mechanism must generalize

---

## Solution 1: Micro-Credentials

**The problem**
A completion certificate proves a video was watched — not that the material
was understood. Employers can't tell which "skills" on a profile are real.

**How this solves it**
Every concept becomes a Micro-Credential: an AI-assigned depth score (0–10)
backed by an evidence log of quoted excerpts from the learner's own
conversation — not a pass/fail checkbox.

**What's different**
Coursera-style platforms are top-down — they tell you a course covered a
skill. Talent Bridge is bottom-up — it reports *how well*, and every score
traces back to evidence anyone can check. No black box.

---

## Inside a Micro-Credential

- The atomic, scored unit of a course: one concept / skill
- Contains: depth score (0–10), exercise/scenario history, competency
  summary
- The score updates as new exercises complete — see Competency Decay

---

## Depth Score

AI-assigned, 0–10, derived from three dimensions of a section conversation:

- **Speed** to real understanding
- **Quality** of the learner's own explanation
- **Sharpness** of the learner's follow-up questions

Every score carries an evidence log — quoted excerpts from the actual
conversation, not an opaque number.

*Open question: the exact formula combining the three dimensions is not yet
defined.*

---

## Competency Decay

- **−0.5 every 3 months** while unemployed, off a 0–10 scale, floors at 0
- Refreshes upward on newer completed exercises
- **Frozen** while employed in a role that uses the skill — no decay

**Example:** MC at 8.0 → unemployed 3 months → 7.5 → 6 months → 7.0.
A new exercise scoring 9.0 at month 4 refreshes the stored score upward
instead of continuing to decay.

---

## Solution 2: Course Creation & Section Gating

**The problem**
Generic curricula don't map to what a specific job actually needs, and
click-through completion (watch → quiz → certificate) doesn't test whether
the learner understood anything.

**How this solves it**
AI designs each course directly from a real job description. Content is
split into sequential, gated sections — a learner can't advance without a
real conversation with the AI instructor, proving genuine understanding.

**What's different**
Scoped "down to the T" to one job, not a fixed catalog course. Progression
is gated by demonstrated understanding, not a quiz, and every AI-drafted
course is validated by a human expert before it reaches a learner.

---

## How a Course Gets Built

- Anchored to a real job description (MVP: hand-picked sample; future:
  live LinkedIn scrape)
- Sections numbered sequentially (1.1, 1.2, 1.3, …) — each unlocks only
  after the previous is complete
- Credential issues only once **every** section is genuinely completed

---

## Section Gating — Worked Example

A learner finishes reading 1.1 ("What is a storage array?"). To unlock 1.2
they must:

- Explain in their own words what a storage array is and why redundancy
  matters
- Answer a follow-up probing question

If they can only repeat memorized phrases without engaging the follow-up,
the section stays locked and the AI flags the specific gap for another
attempt.

---

## Solution 3: Sandbox Incident Simulation
### *(exploratory)*

**The problem**
Conceptual understanding alone doesn't prove someone can troubleshoot a
real incident under real conditions — and tests like HackerRank only
measure isolated problem-solving under exam pressure, in one sitting.

**How this solves it**
Learners get a cloud workspace mocking a real data-center incident
(storage array failure, latency spike) and must troubleshoot it back to
working order, verified by an automated test suite.

**What's different**
Measures applied skill on real infrastructure patterns tied to the job,
not a timed abstract puzzle — though this piece is still exploratory.

---

## Inside the Sandbox

- Cloud workspace issued via K8s; incident triggered via Terraform
  configuration
- Learner troubleshoots, then a test suite confirms the exercise is
  complete
- **The hard part:** most storage/network vendor platforms have no public
  simulator (e.g. Dell PowerMax) or require a vendor support account
  (e.g. NetApp's ONTAP Simulator) — credible mocking needs partnerships
  with each software provider to provision training licenses/accounts,
  not just more engineering time
- Recorded/replayed or AI-generated fake output looks plausible but gets
  subtle details wrong — undermines the "prove real understanding" premise

---

## Employer Matching

- Employer lists required course credentials for a role
- System returns every candidate who **genuinely earned** them — all
  sections, all credentials issued
- No ranking algorithm, no black box — rule-based on verified prerequisites
- Employer sees linked exercise history and summaries, not raw personal data

**Example:** Role requires `storage-fundamentals-101` +
`network-troubleshooting-201`. Candidate A completed both → matched.
Candidate B completed only sections 2.1–2.2 of the second course → not
matched, regardless of resume strength.

---

## MVP Scope Boundaries

| In MVP scope | Out of scope (future) |
|---|---|
| Solution 1 — MCs, depth scoring, decay | Solution 3 full sandbox (K8s + Terraform) |
| Solution 2 — gated course creation | Live LinkedIn scraping pipeline |
| Single-server stack (FastAPI + Claude via OpenRouter + SQLite) | Horizontal scaling / distributed infra |
| Human review of every AI-drafted course | Human appeal workflow for disputed evaluations |
| Recruiter-facing skill tracing | Formal legal PDPA sign-off |

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Python + FastAPI | Routes every learner message to Claude and back |
| AI Engine | Claude, via OpenRouter | Socratic teaching, evaluation, course drafting |
| Database | SQLite | One file, no separate server, reliable at this scale |
| Frontend | Plain HTML/CSS/JS | Nothing to break live in a demo |

Direct model calls to Claude via OpenRouter, not a heavier agent framework —
precise control over teaching/evaluation prompts without unnecessary
complexity, and the model/provider stays a config value instead of a
hardcoded SDK dependency.

---

## Key Decisions (Load-Bearing)

- Bottom-up competency signal, not top-down completion
- Full transparency to evidence — no black-box scores
- Competency decay models real atrophy; frozen while employed
- Sequential gated sections — can't skip ahead
- Human expert reviews every AI-drafted course before publish
- Matching is rule-based on verified prerequisites, not a ranking model

---

## Open Questions

- What's the exact formula combining speed / explanation quality / question
  sharpness into one 0–10 depth score?
- Is the "no PDPA concerns" claim for recruiter-visible tracing actually
  correct under Indonesian law?
- Sandbox realism is a vendor-partnership problem, not an engineering one
  — who owns outreach to NetApp/Dell/etc. for training-account access?
  *(see Roadmap)*
- What does a human-review/appeal path for disputed AI evaluations look
  like? *(post-MVP)*
- How will live LinkedIn job scraping work — rate limits, ToS, freshness?
  *(post-MVP)*

---

## Roadmap: Near-Term (Post-MVP)

- **Section-gating enforcement** — lock section access server-side, not
  just track status (closes the current implementation gap)
- **Human review/appeal workflow** — a recorded, checkable approval gate
  for AI-drafted courses, and a path to contest a disputed evaluation
- **Live LinkedIn job scraping** — replace the MVP's hand-picked sample
  job description with a real, per-user job feed
- **Bahasa Indonesia support** — lower the barrier for Batam's
  SMA/SMK-majority workforce, most of whom aren't native English speakers
- **Formal PDPA legal sign-off** on recruiter-visible skill tracing

---

## Roadmap: Further Out

- **Voice-to-text conversation** — talk through an explanation instead of
  typing it; more natural Socratic dialogue, lower barrier for learners
  less comfortable writing long answers
- **Sandbox incident simulation, revived** — once vendor partnerships
  (NetApp, Dell, etc.) provide real training-account access (see
  *Inside the Sandbox*)
- **Employer analytics dashboard** — skill-gap visibility across an
  entire talent pool, not just per-candidate matching
- **Beyond Batam / data centers** — the course → gated section →
  evidence-based credential mechanism is built to generalize to other
  regions and industries
- **Government program integration** — e.g. Kartu Prakerja,
  SkillsFuture/TeSA — as a verified-competency layer on top of existing
  subsidized training

---

<!-- _class: lead -->

## Closing

> "This isn't about replacing human trainers. It's about giving Batam's
> workforce a fast, honest way to prove they're ready for these new roles —
> and giving employers, whether in Batam or across the strait in Singapore,
> a reason to actually trust that signal."

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Appendix
## Q&A Backup

---

## Isn't scoring learners a privacy concern?

Fully transparent — the learner knows from sign-up that conversations are
evaluated and that evaluation is what employers see. Nothing hidden; that
transparency is itself part of the trust mechanism.

*(PDPA legal verification is still an open item.)*

---

## How would this scale to thousands of users?

Architecture doesn't need to change — every conversation is already an
independent API call, so it scales horizontally.

The real cost driver is AI API usage, which scales with actual usage rather
than fixed infrastructure.

---

## Why not build on an existing platform?

Existing platforms prove content consumption, not understanding — that's
exactly the gap this exists to close.

Direct model calls to Claude via OpenRouter (not a heavier framework) give
precise control over teaching/evaluation prompts without unnecessary
complexity at this stage.

---

## What if the AI evaluation is wrong or unfair?

Every score is backed by a quoted excerpt from what the learner actually
said — evidence-based, not a bare number.

A production version would add a human review/appeal path on top of the
same evidence log *(not built yet)*.
