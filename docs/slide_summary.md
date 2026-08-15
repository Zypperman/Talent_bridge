# Talent Bridge — Slide Content Plan

Content outline for the presentable Marp deck at `slides/slides.md` (run
`npm run preview` inside `slides/` to view it; `npx marp slides.md -o slides.html`
to rebuild the static export).

Compressed to a 3-slide pitch (plus an unnumbered title and an appendix of
Q&A backup slides, which don't count toward the 3).

---

## Slide 0 — Title *(unpaginated)*

**Talent Bridge**
Proving understanding, not attendance.

Notes: Batam data-center hiring, hackathon pitch context.

## Slide 1 — The Problem

Hook quote + condensed problem stats in one slide:

- Hook: "Batam's data-center boom is creating real technical jobs... how do
  you close that gap fast, and how does an employer trust someone is ready?"
- Batam open unemployment 7.68% (50,431 people); only 13.74% tertiary-qualified
- Data centers are capital-, not labour-intensive: 50–150 permanent jobs per
  facility vs. 8,000–12,000 for equivalent manufacturing investment
- Self-taught workers walk away with a "Certificate of Completion" that
  proves a video was watched, not that the material was understood
- Employers are left guessing — resume claims, interviews, platform prestige

## Slide 2 — The Solution

Three-column layout, one column per solution, each compressed to a single
problem/how/differentiator paragraph:

1. **Micro-Credentials** — AI-scored 0–10, evidence-logged, decays while
   unemployed, frozen while employed in the role
2. **Gated Course Creation** — AI builds courses from real job descriptions;
   sections unlock only via a real Socratic conversation; human-reviewed
3. **Sandbox Simulation** *(exploratory)* — cloud workspace mocks a real
   incident, verified by an automated test suite; blocked on vendor
   simulator access, not engineering effort

Plus one line on employer matching: rule-based on verified prerequisites,
no ranking black box.

## Slide 3 — MVP, Tech & What's Next

Two-column layout:

- **Left:** MVP scope (Solutions 1 & 2, FastAPI + Claude/OpenRouter +
  SQLite, human review of every AI draft) + key load-bearing decisions
  (bottom-up signal, full transparency, rule-based matching)
- **Right:** Roadmap — near-term (server-side gating enforcement, appeal
  workflow, live job scraping, Bahasa Indonesia, PDPA sign-off) and further
  out (voice-to-text, sandbox revived, employer analytics, beyond Batam,
  government program integration)

Closes with the same closing quote as before: "This isn't about replacing
human trainers..."

---

## Appendix — Q&A Backup *(unnumbered, not part of the 3)*

Unchanged from the full deck — four backup slides for anticipated
questions:

1. Isn't scoring learners a privacy concern?
2. How would this scale to thousands of users?
3. Why not build on an existing platform?
4. What if the AI evaluation is wrong or unfair?

---

## What got cut / folded from the original 26-slide deck

Everything below was either folded into the 3 slides above (compressed to a
line or a phrase) or dropped as a standalone slide because it was
implementation detail rather than pitch-critical:

- Separate "Who Hurts", "Current Workaround Fails", "Why Now" slides →
  folded into Slide 1's problem bullets
- Separate "Goals" / "Non-Goals" slides → dropped (implicit in the solution
  framing; revive if a reviewer asks)
- "Inside a Micro-Credential", "Depth Score", "Competency Decay" detail
  slides → compressed to one sentence in Slide 2's first column
- "How a Course Gets Built", "Section Gating Worked Example" → compressed
  to one sentence in Slide 2's second column
- "Inside the Sandbox" (K8s/Terraform mechanics, vendor blocker detail) →
  compressed to one sentence in Slide 2's third column
- "Employer Matching" detail + worked example → compressed to one line
  under the solution columns
- "MVP Scope Boundaries" table, "Tech Stack" table → compressed to bullet
  fragments in Slide 3's left column
- "Key Decisions" → compressed to bullet fragments in Slide 3's left column
- "Open Questions" → dropped as a standalone slide (still worth having
  answers ready — see Appendix Q&A backup)
- "Roadmap: Near-Term" / "Roadmap: Further Out" → compressed to bullet
  fragments in Slide 3's right column
- "Closing" → folded into the bottom of Slide 3

If a reviewer wants the full detail on any compressed point, the original
26-slide version is recoverable from git history (`git log -- slides/slides.md`).
