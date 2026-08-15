A design doc written for an agent has a different center of gravity than one written for a team. Humans fill gaps with tribal knowledge and ask you at standup; an agent will either invent an answer or stall. So the doc has to carry more of the context explicitly.

**The core sections**

- **Problem and user** — who hurts, what the current workaround is, why now. One paragraph. This is what lets an agent make sensible micro-decisions you didn't anticipate.
- **Goals and non-goals** — the non-goals matter more with agents than with people. "Don't add auth," "don't refactor the existing parser," "don't optimize for mobile yet." Agents scope-creep enthusiastically.
- **Scope boundaries in concrete terms** — which files, directories, services, or tables are in play, and which are off-limits. Vague scope is where agent work goes sideways.
- **Decisions already made** — with a one-line rationale each. Without this, an agent re-litigates settled questions or quietly picks differently. Rationale matters because it tells the agent whether a decision is load-bearing or arbitrary.
- **Open questions** — explicitly flagged, with what you want the agent to do about them (pick a default and note it? stop and ask?).
- **Interfaces and contracts** — data shapes, function signatures, endpoint paths, event names, error formats. Be literal. This is the single highest-leverage section, because it's what makes independently-produced pieces fit together.
- **Acceptance criteria** — checkable, not aspirational. "Returns 400 with `{error: "..."}` when the token is expired" beats "handles errors gracefully." If a criterion can't be verified by running something or reading output, rewrite it.
- **Worked examples** — two or three concrete input/output pairs, including one edge case and one failure case. Examples resolve ambiguity that prose can't.
- **Constraints** — libraries you must or must not use, performance budgets, style conventions, backward-compat requirements, security or compliance rules.

**Things that are specific to agent readers**

*Escalation rules.* Say when to stop. "If the migration would drop data, stop and ask." "If a change touches more than N files, check in first." Agents default to plowing ahead.

*Verification loop.* How does the agent know it's done and correct? Name the test command, the lint command, the manual check. An agent with a feedback loop self-corrects; one without produces plausible-looking work.

*Sequencing.* If order matters, say so. Agents parallelize or interleave in ways that break assumptions.

*Definitions.* Any internal term, acronym, or overloaded word — define it once. "Account" means different things in different codebases.

**A quick quality test:** hand the doc to someone competent who's never seen the project, with no ability to ask you questions. Wherever they'd have to guess, the agent will guess too — and it'll guess with more confidence and less visible hesitation.

If you tell me what kind of work you're delegating — code, research, content, ops — I can sharpen this into a template that fits.