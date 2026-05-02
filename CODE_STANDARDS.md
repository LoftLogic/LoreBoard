# Loreboard Code Quality Standards

## Python (Backend)

### Structure & Modularity
- One responsibility per module. If a file does two unrelated things, split it.
- Services (`*Service` classes) own business logic. Routes own HTTP concerns only — no business logic in handlers.
- Helpers that are used in more than one place live in a shared `helpers.py`. Single-use utilities stay local.
- No loose scripts in source directories. Entry points belong in `src/main.py` or `src/jobs/worker.py`.

### Patterns & Paradigms
- Dependency injection via FastAPI `Depends()` for all database sessions and services.
- Repository pattern: database access goes through `CanonicalMemory`, `SemanticMemory`, or `WorkingMemory`. Raw `session.execute()` is only acceptable inside those classes and `TelemetryService`.
- Protocol over ABC for pluggable interfaces (e.g. `EmbeddingProvider`). ABCs are for internal hierarchies (e.g. `Agent`).
- Use `dataclasses` or Pydantic models for structured data. Never pass raw `dict` across function boundaries if the shape is known.

### Async
- All database access inside FastAPI routes must be `async`. Never call `asyncio.run()` from within a running event loop.
- Celery tasks are sync entry points — use `asyncio.run()` inside them via the `run_job()` helper. Do not mix async/sync in the same call stack.
- `asyncio.create_task()` for fire-and-forget background work (telemetry persistence). Never block the caller waiting for non-critical I/O.

### Type Safety
- All function signatures must have complete type annotations (parameters + return type).
- No `Any` unless interfacing with a truly untyped third-party API (e.g. raw Anthropic response blocks). Document why with a `# noqa: ANN401` comment.
- Use `from __future__ import annotations` at the top of every module for forward reference support.
- Pydantic models for all external inputs (API request bodies, agent outputs). Never trust raw `dict` from external sources.

### Error Handling
- Errors that callers must handle: raise typed exceptions.
- Errors in fire-and-forget background tasks (e.g. telemetry): log with `log.warning(...)`, never raise. The main path must not fail because telemetry broke.
- Never silence exceptions with a bare `except: pass`. Minimum: `except Exception as exc: log.error(...)`.
- `_get_or_404()` pattern for all route-level entity lookups. No inline `if obj is None: raise HTTPException` duplication.

### Naming
- Classes: `PascalCase`. Functions/variables: `snake_case`. Constants: `SCREAMING_SNAKE`.
- Private helpers and implementation details: prefix with `_`.
- Async functions that are not meant to be called externally: prefix with `_`.
- Database model classes match their table names in singular PascalCase (`JobRecord` → `job_records`).

### Comments & Documentation
- Module-level docstring: one sentence explaining purpose. No novels.
- Class docstring: only if the class name alone doesn't explain it.
- Function docstrings: only for public API methods where the signature doesn't tell the whole story (side effects, non-obvious invariants).
- Inline comments: explain *why*, never *what*. If you find yourself writing `# loop over items`, delete it.
- No TODO/FIXME left in merged code unless it has an associated ticket reference.

### Testing
- Every public service method needs at least one happy-path test and one error/edge-case test.
- Tests hit a real (test) database via the `conftest.py` session fixture. No mocking the DB layer.
- Test files mirror source structure: `tests/test_memory_canonical.py` for `memory/canonical.py`.
- Test function names: `test_<what>_<condition>` (e.g. `test_upsert_chapter_marks_stale`).
- No test should depend on execution order. Each test gets a rolled-back session.

### Imports
- Standard library → third-party → internal. One blank line between each group.
- No wildcard imports (`from x import *`).
- Circular imports are a design smell. Fix the design, not the import (local imports inside functions are a last resort, not a first choice).

---

## TypeScript (Frontend)

### Structure & Modularity
- Pages in `src/pages/`, reusable components in `src/components/`, API calls in `src/api/`, types in `src/types/`.
- One component per file. If a file exports more than one component, they should be tightly coupled sub-components (e.g. `RunRow` inside `Telemetry.tsx`).
- API modules (`src/api/*.ts`) contain only HTTP calls. No state, no UI logic.

### Type Safety
- `strict: true` in `tsconfig.json` — non-negotiable.
- No `any`. Use `unknown` + type guards if the shape is genuinely unknown.
- All props interfaces defined explicitly. No inline `{ prop: type }` for non-trivial shapes.
- API response types defined in `src/types/` and imported into both the API module and the consuming component.

### React Patterns
- Hooks for all stateful logic. No class components.
- `useCallback` for handlers passed as props (avoids unnecessary child re-renders).
- Data fetching in `useEffect` with proper cleanup. Polling via `setInterval` must clear the interval on unmount.
- Sub-components that only render (no state/effects) can be plain functions in the same file.

### Styling
- Tailwind utility classes only. No inline `style={{}}` except for dynamic values that can't be expressed as utilities.
- Color tokens from the `loreboard` palette defined in `tailwind.config.js`. No raw hex values in components.
- Responsive by default: think mobile-first even for internal tools.

### Comments
- Same philosophy as Python: explain *why*, not *what*.
- No commented-out JSX blocks left in merged code. Delete dead code.

---

## Git & CI

- Commits are atomic: one logical change per commit.
- PR titles follow: `<type>: <short description>` where type is `feat`, `fix`, `refactor`, `test`, `docs`, or `chore`.
- All CI checks (ruff, mypy, pytest, tsc, build) must pass before merge.
- New features require corresponding tests in the same PR.
