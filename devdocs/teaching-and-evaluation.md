# Teaching & Evaluation

Everything AI-related lives in
[services/teaching_service/service.py](../services/teaching_service/service.py), which
exposes exactly two RPC actions to the gateway: `generate_teaching_reply` and
`evaluate_section`. Both call the same client/model; the difference is entirely in the
prompt.

## Model & provider

```python
client = OpenAI(api_key=os.getenv("OPENROUTER_KEY"), base_url="https://openrouter.ai/api/v1")
MODEL = "anthropic/claude-sonnet-4-6"
```

The service uses the standard `openai` Python SDK pointed at OpenRouter's
OpenAI-compatible endpoint rather than Anthropic's own SDK — per the
[README](../README.md#tech-stack), this is deliberate so the model/provider is a
config value (change `MODEL` and/or `base_url`), not a hardcoded SDK dependency.
[generate_courses.py](../generate_courses.py) uses the identical client setup and
`MODEL` constant for drafting course content — if you change the model here, change it
there too (there's no shared config; both files hardcode the string independently).

`OPENROUTER_KEY` is read from the environment (`.env`, loaded via `python-dotenv`). If
unset, teaching-service starts fine but every Claude call raises — chat and evaluation
requests will fail with `{"error": "Teaching service is unavailable, please try
again"}` at the gateway (the RPC call times out or the worker returns an error
envelope; see [architecture.md](architecture.md#the-rpc-layer)).

## Socratic teaching (`generate_teaching_reply`)

`TEACHING_SYSTEM_PROMPT` (in
[services/teaching_service/service.py](../services/teaching_service/service.py)) is
formatted with the section's `content` and sent as the `system` message, followed by
the full conversation-so-far as `user`/`assistant` messages. Key constraints baked
into the prompt:

- Stay strictly scoped to *this section's* content — explicitly told not to wander
  into other topics.
- Socratic method: ask diagnostic questions, let the learner explain in their own
  words, correct misconceptions gently — not a lecture.
- One idea per response.
- When it judges the learner has shown real understanding, it says so explicitly and
  tells them they can mark the section complete.

That last point is purely a signal to the learner in the chat UI — **the AI does not
mark anything complete itself**. Completion is a separate, explicit action
(`POST /api/sections/complete`, triggered by the learner clicking "Mark Section
Complete" in `static/index.html`) that runs a second, independent evaluation pass. A
learner can click that button at any point, including before the AI thinks they're
ready — there's no gate on it.

`max_tokens=800` per reply; no streaming — the gateway awaits the full RPC round trip
before returning `{"reply": "..."}` to the browser.

## Evaluation (`evaluate_section`)

Runs once, when `/api/sections/complete` is called. `EVALUATION_PROMPT` is given the
section content plus the *entire* transcript (flattened to `"ROLE: content\n\n"` per
turn) as a single `user` message, and is instructed to return **only JSON**, no
markdown fences:

```json
{
  "speed_score": 0.0,
  "explanation_score": 0.0,
  "question_sharpness_score": 0.0,
  "evidence": "one or two sentences citing specific things the learner said or asked"
}
```

Scoring guide baked into the prompt (each 0.0–1.0):
- **speed_score** — how efficiently genuine understanding was reached; explicitly
  told *not* to reward speed if understanding was shallow.
- **explanation_score** — quality of the learner's own-words explanation, evidence-based.
- **question_sharpness_score** — depth/insight of the learner's own questions; no real
  questions asked → low score.

`evaluate_section` strips a leading/trailing ```` ``` ```` code fence if present (some
models wrap JSON in one despite instructions) and `json.loads`s the result. **If
parsing fails, it does not raise** — it returns all three scores as `None` with
`"evidence": "Evaluation failed to parse"`, and the gateway persists that as-is via
`evaluation.get("speed_score")` etc. (all `.get()`, no validation). A section can end
up `status = 'completed'` in `section_progress` with `NULL` scores this way — worth
knowing if you see blank scores in the admin console or on a candidate's profile;
it means the model didn't return parseable JSON, not that scores were literally zero.
There's no retry.

## Where to change things

- **Prompt wording / scoring rubric**: edit `TEACHING_SYSTEM_PROMPT` or
  `EVALUATION_PROMPT` in
  [services/teaching_service/service.py](../services/teaching_service/service.py).
  Nothing else needs to change — the gateway just forwards whatever comes back.
- **Model or provider**: change `MODEL` (and `base_url`/`api_key` if leaving
  OpenRouter) in both `services/teaching_service/service.py` and
  `generate_courses.py` if you want course generation to match.
- **Response length**: `max_tokens` is set per-call (800 for teaching replies, 500 for
  evaluation) — raise it if replies/evaluations are getting cut off.
- **Timeout**: the gateway's RPC client for teaching is constructed with a 60s timeout
  (`RPCClient("teaching", timeout=60)` in [gateway/main.py](../gateway/main.py)) to
  give Claude calls room; if you see spurious "Teaching service is unavailable"
  errors under load, that's the first place to look.
