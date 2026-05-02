# Loreboard — Feature Inventory

> Update this file when shipping a feature, moving something to in-progress, or adding to the roadmap. Be honest about status — "stub" means the endpoint exists but the agent does nothing useful yet.

---

## Shipped ✅

### Rich Text Editor
- Lexical-based editor with block types: Body, Title, Chapter, Subtitle
- Text formatting: Bold, Italic, Underline
- Custom `SubtitleNode` (scene break / subtitle styling)
- Undo/redo via `HistoryPlugin`
- `OnChangePlugin` for capturing editor state as JSON

### Story & Chapter Management (API)
- Create story, get story
- Create chapter, update chapter content
- Content update automatically marks chapter as `STALE`
- Chapter overrides (key/value, writer-controlled)

### Job System
- Celery + Redis broker with three priority queues (high / default / low)
- `JobRecord` tracking (status, priority, result, error)
- `run_job()` lifecycle helper — PENDING → RUNNING → DONE/FAILED
- Retry with backoff (3 attempts, 10s delay)
- `task_acks_late`, `prefetch_multiplier=1` for reliability

### Orchestrator Agent
- Decomposes a high-level directive into a list of `PlannedJob` objects
- Uses `claude-haiku-4-5-20251001` for fast planning
- Structured JSON output with graceful fallback on parse failure

### Three-Layer Memory
- **Canonical**: PostgreSQL via `CanonicalMemory` — story truth, staleness tracking
- **Semantic**: pgvector (dim=1536) via `SemanticMemory` — entity similarity search
- **Working**: Redis via `WorkingMemory` — per-job ephemeral context with TTL

### Context Assembly
- `ContextAssembler` pulls from all memory layers with per-agent-type depth gating
- `Context.to_prompt_dict()` for safe prompt injection
- Entity anchoring prevention for `EntityExtractor`

### Telemetry (3-Layer)
- **Instrumentation**: `InstrumentedAnthropic` wraps every `messages.create()` — captures tokens, latency, tool calls, full input/output, zero agent code changes needed
- **Collection**: `LlmCall` DB model linked to `AgentRun`; `TelemetryService` for aggregated queries
- **Display**: `/telemetry` dashboard — stats cards, per-agent breakdown, expandable run rows with LLM call detail

### Feedback & Calibration Loop
- Writers rate agent runs (1–5) with notes and structured overrides
- `CalibrationService` aggregates recent feedback into `CalibrationContext`
- Calibration block injected into agent system prompts
- `force_calibration()` endpoint for manual re-calibration

### Flags System
- Agent-generated `StoryFlag` records (type, severity: info/warning/error)
- Per-story and per-chapter flags
- Writer can resolve flags via API

### CI/CD
- GitHub Actions: backend (ruff + mypy + pytest with postgres/redis services)
- GitHub Actions: frontend (tsc --noEmit + vite build)

### Landing Page
- Marketing page with hero section, two feature sections, about section
- Responsive layout, loreboard brand styling

---

## In Progress / Stub ⬜

These endpoints and tasks exist but the agent logic is not yet implemented. Tasks log `task.not_implemented` and return early.

### Chapter Analysis (`analyze_chapter` task)
- Endpoint: `POST /jobs/analyze-chapter/{chapter_id}`
- Expected output: `ChapterAnalysisOutput` — summary, themes, POV character, word count, flags
- Status: Celery task exists, `ChapterAnalyzerAgent` class not yet created

### Entity Extraction (`extract_entities` task)
- Endpoint: `POST /jobs/extract-entities/{chapter_id}`
- Expected output: `EntityExtractionOutput` — list of extracted entities with type, attributes, mention positions
- Should write extracted entities back to canonical memory and trigger semantic embedding
- Status: Celery task exists, `EntityExtractorAgent` class not yet created

### Consistency Check (`check_consistency` task)
- Endpoint: `POST /jobs/check-consistency/{story_id}`
- Expected output: `ConsistencyCheckOutput` — list of `ConsistencyIssue` with type, severity, location
- Issues should be written as `StoryFlag` records
- Status: Celery task exists, `ConsistencyCheckerAgent` class not yet created

### Autofill (`autofill` task)
- Endpoint: via orchestrator dispatch
- Expected output: `AutofillOutput` — ranked suggestions for `___` placeholders
- Uses semantic search to find contextually appropriate completions
- Status: Celery task exists, `AutofillAgent` class not yet created

### Summarizer (`summarize` task)
- Expected output: `SummarizerOutput` — summary at story/chapter/entity scope
- Status: Celery task exists, `SummarizerAgent` class not yet created

---

## Planned / Roadmap 🗓

### Save & Analyze Flow (Frontend ↔ Backend integration)
- Editor currently calls `storiesApi`, `chaptersApi`, `jobsApi` — but these API modules need to be created (currently imported but assumed to exist)
- Wire up real story/chapter persistence from the Editor page

### Entity Profile View
- UI for browsing extracted entities: character sheets, location pages, item descriptions
- Entity detail page showing all mentions across chapters with context snippets
- Entity editing / manual attribute overrides

### Note Web (Planned)
- Visual relationship graph between entities
- Faction/event/map nodes
- AI-assisted relationship extraction from prose

### Version Control (Planned)
- Branch narrative at any chapter
- Compare two versions of a chapter
- Merge branches with conflict resolution
- Full revision history per chapter

### Autofill UI (Planned)
- Writer types `___` in the editor; a suggestion popover appears
- Right-click any word → "Find alternatives" → adjective-driven semantic search
- Inline accept/reject flow

### Consistency Dashboard (Planned)
- Dedicated view for unresolved flags
- Filter by severity, chapter, entity
- One-click resolve with optional note

### Multi-Model Support (Planned)
- Currently hardcoded to Anthropic. Abstract the LLM client behind a provider protocol.
- Per-agent model selection (fast/cheap for orchestration, powerful for consistency checking)

### Export (Planned)
- Export story as Markdown, DOCX, or PDF
- Export entity profiles as structured JSON or wiki pages
