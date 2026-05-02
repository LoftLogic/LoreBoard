# Loreboard — Agent System Reference

> Update this file when adding agents, modifying context assembly logic, changing output schemas, or updating calibration behaviour.

---

## Agent Base (`agents/base.py`)

All agents extend `Agent`:

```python
class MyAgent(Agent):
    agent_type = AgentType.MY_TYPE

    async def _execute(self, context: Context, job_id: str) -> MyAgentOutput:
        system = self._build_system_prompt(context, extra="...")
        response = await self._client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": "..."}],
        )
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return MyAgentOutput(job_id=job_id, success=True, tokens_used=tokens, ...)
```

### What `Agent.run()` does automatically
1. Creates an `AgentRun` record in Postgres (status=`running`).
2. Sets `run_id` on the instrumented client so every `messages.create()` call is linked.
3. Calls `_execute()`.
4. On success: updates `AgentRun` with output, token count, elapsed ms (status=`done`).
5. On failure: updates `AgentRun` with error string (status=`failed`), then re-raises.
6. Clears `run_id` from the client in `finally` regardless.

Never call `_execute()` directly — always call `run()`.

---

## LLM Client (`telemetry/collector.py`)

Every agent gets an `InstrumentedAnthropic` instance as `self._client`. It is a transparent wrapper around `anthropic.AsyncAnthropic` that:
- Intercepts every `messages.create()` call
- Measures latency
- Persists a `LlmCall` row linked to the current `run_id`
- Fires the DB write as a background task — **never blocks the agent**

Do not instantiate `anthropic.AsyncAnthropic` directly in an agent. Always use `self._client`.

---

## Context Assembly (`context/assembler.py`)

```python
context = await assembler.assemble(
    agent_type=AgentType.ENTITY_EXTRACTOR,
    task_description="Extract entities from chapter 3",
    scope=TaskScope(story_id=..., chapter_id=...),
)
```

The assembler pulls from all three memory layers. Pull depth is gated by agent type to prevent anchoring and control token cost:

| Agent | Chapters pulled | Entities pre-loaded | Semantic search |
|---|---|---|---|
| `orchestrator` | All | Yes | No |
| `chapter_analyzer` | Scoped chapter | Yes | Yes |
| `entity_extractor` | Scoped chapter | **No** (avoids anchoring bias) | Yes |
| `consistency_checker` | All | Yes | Yes |
| `autofill` | Scoped chapter | Yes | Yes (on placeholder text) |
| `summarizer` | All | Yes | No |

`context.to_prompt_dict()` serialises everything into a dict for prompt injection.
`context.task_description` is the agent's directive.
`context.chapters` is the list of in-scope `Chapter` objects.

---

## Output Schemas (`output/schemas.py`)

Every `_execute()` must return a subclass of `AgentOutput`.

```
AgentOutput (base)
  run_id, job_id, agent_type, success, reasoning, tokens_used, elapsed_ms, error
  │
  ├── OrchestratorOutput       → planned_jobs: list[PlannedJob]
  ├── EntityExtractionOutput   → chapter_id, entities: list[ExtractedEntity]
  ├── ConsistencyCheckOutput   → story_id, issues: list[ConsistencyIssue], checked_chapters
  ├── ChapterAnalysisOutput    → chapter_id, summary, themes, pov_character, word_count, flags
  ├── AutofillOutput           → placeholder, suggestions: list[AutofillSuggestion]
  └── SummarizerOutput         → scope, scope_id, summary
```

`AgentOutput.run_id` is set by `Agent.run()` after `_execute()` returns — do not set it inside `_execute()`.

---

## Calibration Injection (`feedback/calibration.py`)

Before building the system prompt, agents can retrieve calibration context:

```python
calibration = await CalibrationService(session).get_calibration_context(self.agent_type.value)
extra = calibration_to_prompt_block(calibration)
system = self._build_system_prompt(context, extra=extra)
```

`CalibrationContext` contains:
- `average_rating` — float 1–5
- `avoid_patterns` — list of strings from low-rated runs
- `overrides` — writer-specified key/value adjustments

The orchestrator currently does not inject calibration (it plans, not interprets). All analysis agents should.

---

## Current Agent Status

| Agent | File | Queue | Status |
|---|---|---|---|
| `OrchestratorAgent` | `agents/orchestrator.py` | high | ✅ Implemented |
| `ChapterAnalyzerAgent` | _to be created_ | default | ⬜ Stub in tasks.py |
| `EntityExtractorAgent` | _to be created_ | default | ⬜ Stub in tasks.py |
| `ConsistencyCheckerAgent` | _to be created_ | default | ⬜ Stub in tasks.py |
| `AutofillAgent` | _to be created_ | high | ⬜ Stub in tasks.py |
| `SummarizerAgent` | _to be created_ | low | ⬜ Stub in tasks.py |

---

## Adding a New Agent (Checklist)

1. **Add the type** to `AgentType` enum in `output/schemas.py`.
2. **Add the output schema** — create `MyOutput(AgentOutput)` in `output/schemas.py` with typed fields.
3. **Create the agent** — `agents/my_agent.py` subclassing `Agent`, implement `_execute()`.
   - Use `self._client.messages.create(...)` (instrumented automatically).
   - Use `self._build_system_prompt(context, extra=...)` for consistency.
   - Inject calibration if the agent interprets/analyses content.
4. **Add the Celery task** in `jobs/tasks.py` following the `run_job()` pattern.
5. **Register the queue route** in `jobs/worker.py` task_routes.
6. **Add API endpoint** in `api/routes.py` using `_submit_job()` helper.
7. **Add request/response schemas** to `api/schemas.py` if needed.
8. **Add context assembly depth** entry to the table in `context/assembler.py` and this doc.
9. **Write tests** — at minimum: happy path and one parse/error case.

---

## System Prompt Construction

`_build_system_prompt(context, extra="")` produces:

```
You are a {agent_type} agent for a creative writing assistant.
Story: {title}
Task: {task_description}
Known entities: {comma-separated names}    ← omitted if no entities
Writer overrides in effect: {overrides}    ← omitted if none
{extra}                                    ← per-agent additions
```

For heavy-reasoning agents, append chain-of-thought instructions to `extra`. For structured output agents, append the JSON schema and "Return ONLY valid JSON" to `extra`.
