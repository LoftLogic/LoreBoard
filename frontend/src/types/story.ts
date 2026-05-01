import type { AnalysisState, FlagSeverity, JobStatus } from './api'

export interface Story {
  id: string
  title: string
  meta: Record<string, unknown>
}

export interface Chapter {
  id: string
  story_id: string
  order: number
  title: string | null
  analysis_state: AnalysisState
  content: string
}

export interface ChapterOverrides {
  overrides: Record<string, string>
}

export interface StoryFlag {
  id: string
  flag_type: string
  message: string
  severity: FlagSeverity
  chapter_id: string | null
}

export interface Job {
  id: string
  job_type: string
  status: JobStatus
  priority: number
  result: Record<string, unknown> | null
  error: string | null
}

export interface Entity {
  id: string
  story_id: string
  name: string
  entity_type: string
  attributes: Record<string, unknown>
}

export interface FeedbackRequest {
  run_id: string
  rating: number
  notes?: string
  calibration_data?: Record<string, unknown>
}
