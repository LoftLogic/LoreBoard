# Loreboard — Claude Code Instructions

## Project Layout

```
backend/   FastAPI + Celery + PostgreSQL (asyncpg) + pgvector + Redis
frontend/  React + TypeScript + Tailwind + Vite + Lexical editor
docs/      Architecture and design documentation (see below)
```

- Backend entry point: `backend/src/main.py`
- Celery worker: `backend/src/jobs/worker.py`
- Frontend entry point: `frontend/src/main.tsx`

## Stack Quick Reference

| Layer | Tech |
|---|---|
| API | FastAPI, async SQLAlchemy 2, asyncpg |
| Jobs | Celery + Redis (3 priority queues: high / default / low) |
| Memory | PostgreSQL (canonical), pgvector (semantic), Redis (working) |
| Agents | Anthropic SDK — all agents extend `src/agents/base.Agent` |
| Frontend | Vite, React 18, TypeScript strict, Tailwind, Lexical |

---

## Living Documentation

The `docs/` directory is the authoritative reference for this project. **Read the relevant doc before working in an area. Update it after any change that affects its content.**

| Document | Covers | Update when you... |
|---|---|---|
| `docs/system.md` | Backend architecture, memory layers, job system, DB schema, telemetry, API endpoints | Change any of these |
| `docs/agents.md` | Agent base class, context assembly, output schemas, calibration, adding new agents | Add/modify agents or context logic |
| `docs/frontend.md` | Pages, routing, components, API layer, Lexical editor, hooks, TypeScript config | Add pages, routes, components, API modules, or hooks |
| `docs/style.md` | Color palette, typography, spacing, component patterns, icon conventions | Add Tailwind tokens, establish new UI patterns |
| `docs/features.md` | Shipped features, stubs, planned roadmap | Ship, stub, or plan a feature |

`CODE_STANDARDS.md` defines quality standards for both Python and TypeScript. Update it if standards evolve.

---

## Code Quality Standards

**Before finishing any task, review your changes against `CODE_STANDARDS.md`.**

Key rules to self-check on every edit:

### Python
- [ ] All function signatures have complete type annotations
- [ ] No bare `except:` or silenced exceptions
- [ ] Business logic is in a Service or Agent class, not in a route handler
- [ ] Database access goes through the memory layer (`CanonicalMemory`, `SemanticMemory`, `WorkingMemory`) or `TelemetryService` — not raw `session.execute()` in routes
- [ ] New public service methods have at least one test
- [ ] `from __future__ import annotations` at top of every module
- [ ] Imports ordered: stdlib → third-party → internal
- [ ] No loose scripts or dead code

### TypeScript
- [ ] No `any` — use `unknown` + type guards if needed
- [ ] Props interfaces explicitly defined in `src/types/`
- [ ] API calls live in `src/api/`, not inside components or hooks
- [ ] No inline `style={{}}` for values expressible as Tailwind utilities

### Both
- [ ] Comments explain *why*, not *what*
- [ ] No commented-out code blocks
- [ ] No TODO/FIXME without a ticket reference

---

## Architecture Rules (never break these)

1. **Async boundary**: FastAPI routes are async. Celery tasks are sync and use `run_job()` from `jobs/helpers.py` to bridge into async. Never call `asyncio.run()` inside an already-running event loop.

2. **Agent instrumentation**: All agents use `InstrumentedAnthropic` (via `self._client` on `Agent` base). Never instantiate `anthropic.AsyncAnthropic` directly in an agent.

3. **Telemetry persistence errors must not crash callers**: errors in `_persist_call()` are logged and swallowed, never raised.

4. **Memory layer exclusivity**: Only `CanonicalMemory`, `SemanticMemory`, and `WorkingMemory` write to their respective stores. Agents read context through `ContextAssembler`, never query DB directly.

5. **Pydantic for all agent outputs**: every agent `_execute()` must return a subclass of `AgentOutput`.

---

## Running Locally

```bash
# Backend
cd backend
uvicorn src.main:app --reload

# Celery worker
cd backend
celery -A src.jobs.worker worker --loglevel=info

# Frontend
cd frontend
npm run dev   # → http://localhost:3000
```

---

## Key Files

| Purpose | File |
|---|---|
| DB models | `backend/src/db/models.py` |
| Agent base | `backend/src/agents/base.py` |
| Context assembly | `backend/src/context/assembler.py` |
| LLM instrumentation | `backend/src/telemetry/collector.py` |
| Telemetry queries | `backend/src/telemetry/service.py` |
| Canonical memory | `backend/src/memory/canonical.py` |
| Job helpers | `backend/src/jobs/helpers.py` |
| API routes | `backend/src/api/routes.py` |
