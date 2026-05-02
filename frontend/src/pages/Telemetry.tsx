import { useEffect, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Clock,
  Zap,
} from 'lucide-react'
import { telemetryApi } from '@/api/telemetry'
import type { AgentRunDetail, AgentRunSummary, LlmCall, TelemetrySummary } from '@/types/telemetry'

const TIME_OPTIONS = [
  { label: '24h', hours: 24 },
  { label: '7d', hours: 168 },
  { label: '30d', hours: 720 },
]

const STATUS_CLS: Record<string, string> = {
  done: 'bg-green-100 text-green-700',
  running: 'bg-loreboard-100 text-loreboard-700',
  failed: 'bg-red-100 text-red-700',
  pending: 'bg-gray-100 text-gray-500',
}

export default function Telemetry() {
  const [sinceHours, setSinceHours] = useState(24)
  const [summary, setSummary] = useState<TelemetrySummary | null>(null)
  const [runs, setRuns] = useState<AgentRunSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<AgentRunDetail | null>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      telemetryApi.getSummary(sinceHours),
      telemetryApi.listRuns({ limit: 100 }),
    ])
      .then(([s, r]) => {
        setSummary(s)
        setRuns(r)
      })
      .finally(() => setLoading(false))
  }, [sinceHours])

  const toggleRun = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null)
      setDetail(null)
      return
    }
    setExpandedId(id)
    setDetail(null)
    telemetryApi.getRun(id).then(setDetail)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Activity size={20} className="text-loreboard-600" />
          <h1 className="text-lg font-semibold text-gray-900">Telemetry</h1>
        </div>
        <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
          {TIME_OPTIONS.map((o) => (
            <button
              key={o.hours}
              onClick={() => setSinceHours(o.hours)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                sinceHours === o.hours
                  ? 'bg-white text-loreboard-700 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {o.label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-6 space-y-6">
        {loading ? (
          <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
            Loading…
          </div>
        ) : (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-4 gap-4">
              <StatCard
                label="Total Runs"
                value={summary?.total_runs ?? 0}
                icon={<Activity size={16} />}
              />
              <StatCard
                label="Total Tokens"
                value={fmtTokens(summary?.total_tokens ?? 0)}
                icon={<Zap size={16} />}
              />
              <StatCard
                label="Errors"
                value={summary?.error_count ?? 0}
                icon={<AlertTriangle size={16} />}
                warn={(summary?.error_count ?? 0) > 0}
              />
              <StatCard
                label="Error Rate"
                value={
                  summary && summary.total_runs > 0
                    ? `${((summary.error_count / summary.total_runs) * 100).toFixed(1)}%`
                    : '0%'
                }
                icon={<AlertTriangle size={16} />}
                warn={(summary?.error_count ?? 0) > 0}
              />
            </div>

            {/* Per-agent breakdown */}
            {summary && summary.by_agent.length > 0 && (
              <section className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <SectionHeader>By Agent Type</SectionHeader>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-gray-100 text-xs uppercase tracking-wide">
                      <th className="px-6 py-3 font-medium">Agent</th>
                      <th className="px-6 py-3 font-medium">Runs</th>
                      <th className="px-6 py-3 font-medium">Tokens</th>
                      <th className="px-6 py-3 font-medium">Avg Latency</th>
                      <th className="px-6 py-3 font-medium">Errors</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.by_agent.map((row) => (
                      <tr key={row.agent_type} className="border-b border-gray-50 hover:bg-gray-50">
                        <td className="px-6 py-3">
                          <AgentBadge type={row.agent_type} />
                        </td>
                        <td className="px-6 py-3 text-gray-700">{row.run_count}</td>
                        <td className="px-6 py-3 text-gray-700">{fmtTokens(row.total_tokens)}</td>
                        <td className="px-6 py-3 text-gray-500">{row.avg_latency_ms}ms</td>
                        <td className="px-6 py-3">
                          {row.error_count > 0 ? (
                            <span className="text-red-600 font-medium">{row.error_count}</span>
                          ) : (
                            <span className="text-gray-300">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}

            {/* Recent runs */}
            <section className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <SectionHeader>Recent Runs ({runs.length})</SectionHeader>
              {runs.length === 0 ? (
                <div className="px-6 py-12 text-center text-gray-400 text-sm">
                  No agent runs yet.
                </div>
              ) : (
                <div className="divide-y divide-gray-50">
                  {runs.map((run) => (
                    <RunRow
                      key={run.id}
                      run={run}
                      expanded={expandedId === run.id}
                      detail={expandedId === run.id ? detail : null}
                      onToggle={() => toggleRun(run.id)}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Run row + expandable LLM calls
// ---------------------------------------------------------------------------

function RunRow({
  run,
  expanded,
  detail,
  onToggle,
}: {
  run: AgentRunSummary
  expanded: boolean
  detail: AgentRunDetail | null
  onToggle: () => void
}) {
  const Chevron = expanded ? ChevronDown : ChevronRight
  return (
    <div>
      <button
        className="w-full px-5 py-3 flex items-center gap-3 hover:bg-gray-50 text-sm text-left"
        onClick={onToggle}
      >
        <Chevron size={13} className="text-gray-400 shrink-0" />
        <AgentBadge type={run.agent_type} />
        <span
          className={`text-xs px-2 py-0.5 rounded font-medium shrink-0 ${STATUS_CLS[run.status] ?? 'bg-gray-100 text-gray-500'}`}
        >
          {run.status}
        </span>
        <span className="flex items-center gap-1 text-gray-500 text-xs shrink-0">
          <Zap size={11} />
          {fmtTokens(run.tokens_used)}
        </span>
        <span className="flex items-center gap-1 text-gray-500 text-xs shrink-0">
          <Clock size={11} />
          {run.elapsed_ms}ms
        </span>
        {run.error && (
          <span className="text-red-400 text-xs truncate max-w-xs" title={run.error}>
            {run.error}
          </span>
        )}
        <span className="text-gray-400 text-xs ml-auto shrink-0">
          {run.started_at ? fmtRelative(run.started_at) : '—'}
        </span>
      </button>

      {expanded && (
        <div className="bg-gray-50 border-t border-gray-100 px-8 py-4">
          {!detail ? (
            <p className="text-gray-400 text-sm">Loading…</p>
          ) : detail.llm_calls.length === 0 ? (
            <p className="text-gray-400 text-sm">No LLM calls recorded for this run.</p>
          ) : (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
                LLM Calls ({detail.llm_calls.length})
              </p>
              {detail.llm_calls.map((call) => (
                <LlmCallCard key={call.id} call={call} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function LlmCallCard({ call }: { call: LlmCall }) {
  const [open, setOpen] = useState(false)
  const Chevron = open ? ChevronDown : ChevronRight

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <button
        className="w-full px-4 py-2.5 flex items-center gap-3 text-sm hover:bg-gray-50"
        onClick={() => setOpen((v) => !v)}
      >
        <Chevron size={12} className="text-gray-400 shrink-0" />
        <span className="font-mono text-xs text-gray-600 shrink-0">{call.model}</span>
        <span className="text-xs text-loreboard-600 shrink-0">
          ↑ {call.input_tokens} in
        </span>
        <span className="text-xs text-loreboard-400 shrink-0">
          ↓ {call.output_tokens} out
        </span>
        <span className="text-xs text-gray-400 shrink-0">{call.latency_ms}ms</span>
        {call.tool_calls.length > 0 && (
          <span className="bg-amber-100 text-amber-700 text-xs px-2 py-0.5 rounded shrink-0">
            {call.tool_calls.length} tool call{call.tool_calls.length > 1 ? 's' : ''}
          </span>
        )}
        <span className="text-gray-400 text-xs ml-auto shrink-0">
          {call.stop_reason ?? '—'}
        </span>
      </button>

      {open && (
        <div className="border-t border-gray-100 grid grid-cols-2 divide-x divide-gray-100">
          <div className="p-4 overflow-hidden">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
              Input
            </p>
            <pre className="text-xs text-gray-700 whitespace-pre-wrap break-all max-h-56 overflow-y-auto">
              {fmtInput(call.input_messages)}
            </pre>
          </div>
          <div className="p-4 overflow-hidden">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
              Output
            </p>
            <pre className="text-xs text-gray-700 whitespace-pre-wrap break-all max-h-56 overflow-y-auto">
              {fmtOutput(call.output_content)}
            </pre>
            {call.tool_calls.length > 0 && (
              <div className="mt-3 space-y-1">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                  Tool Calls
                </p>
                {call.tool_calls.map((tc, i) => (
                  <div key={i} className="font-mono text-xs bg-amber-50 rounded p-2">
                    <span className="text-amber-700 font-bold">{tc.name}</span>
                    {'  '}
                    <span className="text-gray-600">{JSON.stringify(tc.input, null, 2)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Shared UI primitives
// ---------------------------------------------------------------------------

function StatCard({
  label,
  value,
  icon,
  warn,
}: {
  label: string
  value: string | number
  icon: React.ReactNode
  warn?: boolean
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 px-5 py-4">
      <div className="flex items-center gap-2 text-gray-400 mb-2">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
      </div>
      <div className={`text-2xl font-bold ${warn ? 'text-red-600' : 'text-gray-900'}`}>
        {value}
      </div>
    </div>
  )
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-6 py-4 border-b border-gray-100">
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">{children}</h2>
    </div>
  )
}

function AgentBadge({ type }: { type: string }) {
  return (
    <span className="font-mono text-xs text-loreboard-700 bg-loreboard-50 px-2 py-0.5 rounded shrink-0">
      {type}
    </span>
  )
}

// ---------------------------------------------------------------------------
// Formatting helpers
// ---------------------------------------------------------------------------

function fmtTokens(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`
  return String(n)
}

function fmtRelative(iso: string): string {
  const ms = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(ms / 60_000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  return `${Math.floor(hrs / 24)}d ago`
}

function fmtInput(input: LlmCall['input_messages']): string {
  const parts: string[] = []
  if (input.system) parts.push(`[SYSTEM]\n${input.system}`)
  for (const msg of input.messages) {
    const body =
      typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content, null, 2)
    parts.push(`[${msg.role.toUpperCase()}]\n${body}`)
  }
  return parts.join('\n\n')
}

function fmtOutput(content: LlmCall['output_content']): string {
  return content
    .filter((b) => b.type === 'text')
    .map((b) => b.text ?? '')
    .join('\n')
    .trim() || '(no text output)'
}
