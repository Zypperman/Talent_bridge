---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Talent Bridge'
style: |
  section {
    font-size: 24px;
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
    font-size: 20px;
  }
  footer {
    font-size: 16px;
    color: #999;
  }
  h2 {
    margin-top: 0;
  }
  h3 {
    font-size: 22px;
    margin-bottom: 4px;
  }
  blockquote {
    font-size: 20px;
  }
  .cols-3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 8px;
  }
  .cols-3 p, .cols-3 ul {
    font-size: 16px;
    margin: 4px 0;
  }
  .cols-3 ul {
    padding-left: 18px;
  }
  .cols-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-top: 8px;
  }
  .cols-2 ul {
    font-size: 18px;
  }
  .note {
    font-size: 16px;
    color: #777;
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

## The Problem

> "Batam's data-center boom is creating real technical jobs — but most of
> Batam's workforce is in operational roles, not the specialized engineering
> roles this boom needs. How do you close that gap fast, and how does an
> employer actually trust that someone is ready?"

- Batam open unemployment: **7.68%** in 2024 (50,431 people) — only **13.74%**
  of the workforce holds tertiary qualifications
- Data centers are capital-, not labour-intensive: a 50MW facility employs
  only **50–150** people once operational (vs. 8,000–12,000 for equivalent
  manufacturing) — Rp120 trillion of investment barely touches the unemployed
- Workers self-teach via YouTube/Coursera/Udemy and walk away with a
  **"Certificate of Completion"** that proves a video was watched, not that
  the material was understood
- Employers are left guessing — resume claims, interviews, platform prestige —
  none of which measure competency directly

---

## The Solution
### Learning through real conversation, not content consumption.

<div class="cols-3">
<div>

### 1. Micro-Credentials
Every concept is scored 0–10 by AI, backed by an evidence log of quoted
transcript excerpts — not a pass/fail checkbox. Decays −0.5 every 3 months
while unemployed; **frozen** while employed in the role.

</div>
<div>

### 2. Gated Course Creation
AI builds each course straight from a real job description. Sections unlock
only after a real Socratic conversation proves understanding — can't skip
ahead, can't fake it. Every AI draft is human-reviewed before publish.

</div>
<div>

### 3. Sandbox Simulation
*(exploratory)*
Cloud workspace mocks a real incident (storage failure, latency spike); the
learner troubleshoots it, verified by an automated test suite. Blocked on
vendor simulator access (NetApp/Dell) — a partnership problem, not an
engineering one.

</div>
</div>

**Employer matching:** rule-based on verified prerequisites — every candidate
who *genuinely earned* the required credentials, no ranking black box.

---

## MVP, Tech & What's Next

<div class="cols-2">
<div>

**MVP scope**
- Solutions 1 & 2 — micro-credentials + gated course creation
- FastAPI + Claude (via OpenRouter) + SQLite; plain HTML/CSS/JS frontend
- Human review of every AI-drafted course
- Sandbox, live LinkedIn scraping, horizontal scaling → post-MVP

**Key decisions**
- Bottom-up competency signal, not top-down completion
- Full transparency to evidence — no black-box scores
- Matching stays rule-based on verified prerequisites, not a ranking model

</div>
<div>

**Roadmap**
- *Near-term:* server-side gating enforcement, human appeal workflow, live
  job scraping, Bahasa Indonesia support, formal PDPA sign-off
- *Further out:* voice-to-text conversation, sandbox revived via vendor
  partnerships, employer analytics dashboard, beyond Batam/data centers,
  government program integration (Kartu Prakerja, SkillsFuture/TeSA)

</div>
</div>

> "This isn't about replacing human trainers. It's about giving Batam's
> workforce a fast, honest way to prove they're ready — and giving employers,
> in Batam or across the strait in Singapore, a reason to trust that signal."

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
