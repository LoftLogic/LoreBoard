# Loreboard — Design System & Style Guide

> Update this file when adding Tailwind tokens, changing component patterns, or establishing new UI conventions.

---

## Color Palette

Defined in `frontend/tailwind.config.js`. Use these token names everywhere — no raw hex values in components.

### Primary — Loreboard Purple

| Token | Hex | Usage |
|---|---|---|
| `loreboard-50` | `#faf5ff` | Page backgrounds, subtle fills |
| `loreboard-100` | `#f3e8ff` | Active button backgrounds, badges |
| `loreboard-200` | `#e9d5ff` | Hover states on light surfaces |
| `loreboard-300` | `#d8b4fe` | Disabled text, subtle borders |
| `loreboard-400` | `#c084fc` | Secondary text, muted icons |
| `loreboard-500` | `#a855f7` | **Primary interactive** (buttons, links, focus rings) |
| `loreboard-600` | `#9333ea` | Primary button hover, headings |
| `loreboard-700` | `#7e22ce` | Active/pressed states, dark text on light purple |
| `loreboard-800` | `#6b21a8` | Dark surfaces |
| `loreboard-900` | `#581c87` | Very dark surfaces |
| `loreboard-950` | `#3b0764` | Footer, nav backgrounds |

### Accent Colors

| Token | Hex | Usage |
|---|---|---|
| `accent-gold` | `#fbbf24` | Warnings, highlights, tool calls |
| `accent-rose` | `#f43f5e` | Errors, destructive actions |
| `accent-teal` | `#14b8a6` | Success states, entity mentions |

### Semantic Colors (Tailwind defaults)
- Errors/danger: `red-600` / `red-100` for text/backgrounds
- Success: `green-600` / `green-100`
- Neutral UI chrome: `gray-50` through `gray-900`
- Borders: `gray-100` (subtle), `gray-200` (standard), `gray-300` (prominent)

---

## Typography

Defined in `tailwind.config.js` via `fontFamily` extension.

| Family | Fonts | Tailwind class | Usage |
|---|---|---|---|
| Serif | Merriweather, Georgia | `font-serif` | Story titles, chapter headings, prose content |
| Sans | Inter, system-ui | `font-sans` (default) | UI chrome, labels, navigation |
| Mono | system mono | `font-mono` | Agent type badges, code, IDs, tech labels |

### Scale conventions
- Page titles: `text-2xl font-bold` or `text-xl font-semibold`
- Section headers: `text-sm font-semibold uppercase tracking-wide text-gray-500`
- Body: `text-sm text-gray-700`
- Captions / labels: `text-xs text-gray-400`
- Code / IDs: `text-xs font-mono`

---

## Spacing & Layout

- Page max-width: `max-w-7xl mx-auto px-8`
- Card padding: `px-6 py-4` (header), `px-6 py-3` (table rows)
- Section vertical gaps: `space-y-6` between major sections
- Button padding: `px-5 py-2` (standard), `px-3 py-1` (compact), `px-2 py-0.5` (badge)

---

## Shadows & Effects

| Token | Value | Usage |
|---|---|---|
| `shadow-purple-glow` | `0 0 20px rgba(168,85,247,0.3)` | Hero card, primary CTA hover |
| `shadow-sm` | default | Tab active state, small cards |
| `shadow-xl` | default | Feature icon cards |

Gradient backgrounds: `bg-gradient-to-br from-loreboard-50 to-white` for page backgrounds. `bg-gradient-to-r from-loreboard-600 to-loreboard-500` for brand text/icons.

---

## Component Patterns

### Buttons

```tsx
// Primary
className="bg-loreboard-600 hover:bg-loreboard-700 text-white px-5 py-2 rounded-lg font-medium text-sm shadow-lg hover:shadow-purple-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed"

// Ghost / icon button
className="p-2 rounded transition-colors text-gray-600 hover:bg-gray-100"

// Active/selected icon button
className="p-2 rounded transition-colors bg-loreboard-100 text-loreboard-700"

// Compact tab button
className="px-3 py-1 rounded-md text-sm font-medium transition-colors bg-white text-loreboard-700 shadow-sm"   // active
className="px-3 py-1 rounded-md text-sm font-medium transition-colors text-gray-500 hover:text-gray-700"       // inactive
```

### Badges

```tsx
// Agent type badge (monospace)
className="font-mono text-xs text-loreboard-700 bg-loreboard-50 px-2 py-0.5 rounded"

// Status badges
done:    "bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded font-medium"
running: "bg-loreboard-100 text-loreboard-700 text-xs px-2 py-0.5 rounded font-medium"
failed:  "bg-red-100 text-red-700 text-xs px-2 py-0.5 rounded font-medium"
pending: "bg-gray-100 text-gray-500 text-xs px-2 py-0.5 rounded font-medium"

// Tool call badge
className="bg-amber-100 text-amber-700 text-xs px-2 py-0.5 rounded"
```

### Cards

```tsx
// Standard content card
className="bg-white rounded-xl border border-gray-200 overflow-hidden"

// Stat card
className="bg-white rounded-xl border border-gray-200 px-5 py-4"

// Editor card (with glow)
className="bg-white rounded-xl shadow-purple-glow overflow-hidden"
```

### Tables

Section header row pattern:
```tsx
<div className="px-6 py-4 border-b border-gray-100">
  <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Title</h2>
</div>
```

Table header row:
```tsx
<tr className="text-left text-gray-400 border-b border-gray-100 text-xs uppercase tracking-wide">
  <th className="px-6 py-3 font-medium">Column</th>
</tr>
```

Table data row:
```tsx
<tr className="border-b border-gray-50 hover:bg-gray-50">
  <td className="px-6 py-3 text-sm text-gray-700">...</td>
</tr>
```

### Dividers

```tsx
// Vertical (toolbar separator)
<div className="h-5 w-px bg-gray-300 mx-1" />

// Horizontal (section separator)
<div className="divide-y divide-gray-50">
```

---

## Icons

All icons from `lucide-react`. Standard sizes:
- Page-level icon: `size={20}` or `size={22}`
- Inline / row icon: `size={16}`
- Micro / badge icon: `size={12}` or `size={13}`

Common icon associations:
- Activity → telemetry, monitoring
- Zap → tokens, energy, save+analyze
- AlertTriangle → errors, warnings
- CheckCircle → success, resolved
- Clock → latency, timing
- ChevronRight / ChevronDown → expand/collapse
- Search → search
- Bold / Italic / Underline → text formatting (Lexical toolbar)
- Feather → writing, the app brand

---

## Animations

| Token | Value | Usage |
|---|---|---|
| `animate-spin` | default | Loading spinners (`Loader2` icon) |
| `animate-pulse` | default | Skeleton loaders |
| `animation-pulse-soft` | `pulse 3s ease infinite` | Subtle ambient pulse |
| `animation-slide-in` | `translateX -10px → 0, opacity 0 → 1, 0.3s` | Panel/drawer entry |

---

## Accessibility Conventions

- All icon-only buttons must have `title="Description"`.
- Use semantic HTML (`<button>` not `<div onClick>`).
- `disabled` attribute on buttons that should not be clickable — Tailwind handles `disabled:opacity-50 disabled:cursor-not-allowed`.
- Expandable rows use `<button>` wrapping the entire row for keyboard accessibility.
