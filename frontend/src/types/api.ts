/** Shared API-level primitives. */

export type JobStatus = 'pending' | 'running' | 'done' | 'failed' | 'cancelled'
export type AnalysisState = 'pending' | 'analyzed' | 'stale'
export type EntityType = 'character' | 'location' | 'item' | 'event' | 'concept' | 'custom'
export type FlagSeverity = 'info' | 'warning' | 'error'

/** FastAPI validation error shape (422). */
export interface ApiValidationError {
  detail: Array<{ loc: string[]; msg: string; type: string }>
}
