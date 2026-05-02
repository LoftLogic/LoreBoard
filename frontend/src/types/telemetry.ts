export interface LlmCall {
  id: string
  model: string
  input_tokens: number
  output_tokens: number
  latency_ms: number
  stop_reason: string | null
  tool_calls: Array<{ id: string; name: string; input: Record<string, unknown> }>
  input_messages: {
    system: string
    messages: Array<{ role: string; content: string | unknown[] }>
  }
  output_content: Array<{ type: string; text?: string; name?: string }>
  created_at: string | null
}

export interface AgentRunSummary {
  id: string
  job_id: string
  agent_type: string
  status: string
  tokens_used: number
  elapsed_ms: number
  error: string | null
  started_at: string | null
  finished_at: string | null
  llm_call_count: number
}

export interface AgentRunDetail extends AgentRunSummary {
  input_data: Record<string, unknown>
  output_data: Record<string, unknown> | null
  llm_calls: LlmCall[]
}

export interface AgentStat {
  agent_type: string
  run_count: number
  total_tokens: number
  avg_latency_ms: number
  error_count: number
}

export interface TelemetrySummary {
  total_runs: number
  total_tokens: number
  error_count: number
  since_hours: number
  by_agent: AgentStat[]
}
