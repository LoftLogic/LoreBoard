# Loreboard — Frontend Architecture

> Update this file when adding pages, routes, components, API modules, hooks, or changing the Lexical editor setup.

---

## Stack

| Tool | Version | Purpose |
|---|---|---|
| Vite | 5.4 | Build tool and dev server |
| React | 18 | UI framework |
| TypeScript | 5.6 | Type safety (`strict: true`) |
| Tailwind CSS | 3.x | Styling |
| Lexical | 0.21.0 | Rich text editor |
| React Router | 6.x | Client-side routing |
| Axios | 1.x | HTTP client |
| Lucide React | latest | Icon library |

---

## Directory Structure

```
frontend/src/
├── api/          HTTP call modules — one file per backend resource
│   ├── client.ts     Axios instance (base URL, interceptors)
│   ├── chapters.ts
│   ├── jobs.ts
│   ├── stories.ts
│   └── telemetry.ts
├── components/
│   └── editor/   Lexical editor components
│       ├── LexicalEditor.tsx   Composer + plugins
│       ├── Toolbar.tsx         Block type selector + formatting buttons
│       └── nodes.ts            Custom node definitions (SubtitleNode)
├── hooks/
│   └── useJob.ts   Polling hook for job status
├── pages/
│   ├── Editor.tsx      Rich text editor + save/analyze flow
│   ├── Landing.tsx     Marketing landing page
│   └── Telemetry.tsx   Agent run monitoring dashboard
├── types/
│   ├── api.ts          Shared enums (AnalysisState, JobStatus, etc.)
│   ├── story.ts        Story, Chapter, Entity, Job interfaces
│   └── telemetry.ts    AgentRunSummary, AgentRunDetail, LlmCall, TelemetrySummary
├── App.tsx             Route definitions
├── main.tsx            React entry point
└── vite-env.d.ts       Vite ImportMeta type augmentation
```

---

## Routing

Defined in `App.tsx`:

| Path | Component | Notes |
|---|---|---|
| `/` | `Landing` | Marketing page |
| `/editor` | `Editor` | New story session |
| `/editor/:storyId` | `Editor` | Resume existing story |
| `/telemetry` | `Telemetry` | Agent monitoring dashboard |

Add new routes to `App.tsx`. Import pages lazily if the bundle gets large.

---

## API Layer (`src/api/`)

All HTTP calls go through the shared Axios instance in `api/client.ts`:
- `baseURL`: `VITE_API_URL` env var, falls back to `/api/v1` (Vite dev proxy forwards to `localhost:8000`).
- Timeout: 30s.
- Response interceptor: unwraps `error.response.data.detail` into a plain `Error`.

Each resource has its own module (`stories.ts`, `chapters.ts`, etc.) that exports a plain object of async functions. No state lives in API modules.

```typescript
// Pattern
export const storiesApi = {
  create: (title: string) =>
    api.post<StoryResponse>('/stories', { title }).then(r => r.data),
  get: (id: string) =>
    api.get<StoryResponse>(`/stories/${id}`).then(r => r.data),
}
```

---

## State Management

Currently local state only (`useState`, `useReducer`). No global store (no Zustand, Redux, or Context API for shared state yet).

Rules:
- Page-level state stays in the page component.
- Derived/computed values are plain variables, not state.
- Server state (job status, story data) is fetched on mount and updated via polling (`useJob`) or re-fetch after mutations.

If global state becomes necessary, prefer Zustand over Context API (simpler, no prop-drilling solution needed).

---

## Hooks (`src/hooks/`)

### `useJob(jobId, intervalMs?)`
Polls `jobsApi.get(jobId)` every `intervalMs` (default 2000ms). Stops automatically when the job reaches a terminal state (`done | failed | cancelled`). Returns `{ job, error, isTerminal }`.

Cleanup: clears the interval on unmount and on terminal state.

Pattern for adding new polling hooks: mirror `useJob` — manage the interval ref, always clear in cleanup, stop on terminal condition.

---

## Lexical Editor (`src/components/editor/`)

### `LexicalEditor.tsx`
Wraps `LexicalComposer` with:
- `RichTextPlugin` + `ContentEditable`
- `HistoryPlugin` (undo/redo)
- `OnChangePlugin` (calls `props.onChange` on every state change)
- Registered nodes: `HeadingNode` + all entries in `CUSTOM_NODES`

Props: `onChange: (state: EditorState) => void`, `placeholder?: string`

### `Toolbar.tsx`
Block type selector (Body/Title/Chapter/Subtitle) and text format buttons (Bold/Italic/Underline). Reads selection state via `editor.registerUpdateListener` to keep format buttons in sync with cursor position.

Block types map to:
- `basic` → `$createParagraphNode()`
- `title` → `$createHeadingNode('h1')`
- `chapter` → `$createHeadingNode('h2')`
- `subtitle` → `$createSubtitleNode()` (custom node)

### `nodes.ts`
`SubtitleNode` — extends `HeadingNode` (tag `h4`), styled as `text-sm text-loreboard-400 font-mono tracking-widest uppercase`. Used for scene breaks and chapter subtitles.

`CUSTOM_NODES: Klass<LexicalNode>[]` — register all custom nodes here; `LexicalEditor.tsx` spreads this into the `nodes` prop.

When adding a new custom node:
1. Define the class in `nodes.ts` extending an appropriate Lexical base.
2. Implement `getType()`, `clone()`, `createDOM()`, `importJSON()`, `exportJSON()`.
3. Export a `$createMyNode()` factory.
4. Add the class to `CUSTOM_NODES`.

---

## TypeScript Configuration

`tsconfig.json` settings worth knowing:
- `"moduleResolution": "bundler"` — required for Vite. Do not change to `node`.
- `"allowImportingTsExtensions": true` — enables `.ts` / `.tsx` imports without extension stripping.
- `"noUnusedLocals": true`, `"noUnusedParameters": true` — enforced. Delete unused imports immediately.
- `"paths": { "@/*": ["src/*"] }` — use `@/` alias for all internal imports.

`tsconfig.node.json` is separate and covers only `vite.config.ts`. Do not include `vite.config.ts` in the main `tsconfig.json`.

---

## Vite Configuration (`vite.config.ts`)

- Dev server on port 3000.
- Proxy: `/api` → `http://localhost:8000` (eliminates CORS in development).
- Path alias: `@` → `src/`.

---

## Adding a New Page

1. Create `src/pages/MyPage.tsx`.
2. Add route in `App.tsx`.
3. If it needs API data, add/extend a module in `src/api/`.
4. Add types to `src/types/` if the shape is new.
5. Update this doc.
