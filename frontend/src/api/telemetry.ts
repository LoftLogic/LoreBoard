import { api } from './client'
import type { AgentRunDetail, AgentRunSummary, TelemetrySummary } from '@/types/telemetry'

export const telemetryApi = {
  listRuns: (params?: { agent_type?: string; limit?: number; offset?: number }) =>
    api.get<AgentRunSummary[]>('/telemetry/runs', { params }).then((r) => r.data),

  getRun: (runId: string) =>
    api.get<AgentRunDetail>(`/telemetry/runs/${runId}`).then((r) => r.data),

  getSummary: (sinceHours = 24) =>
    api
      .get<TelemetrySummary>('/telemetry/summary', { params: { since_hours: sinceHours } })
      .then((r) => r.data),
}
