import { api } from './client'
import type { Job } from '@/types/story'

export const jobsApi = {
  get: (jobId: string) =>
    api.get<Job>(`/jobs/${jobId}`).then((r) => r.data),

  listForStory: (storyId: string) =>
    api.get<Job[]>(`/jobs/story/${storyId}`).then((r) => r.data),

  orchestrate: (storyId: string, directive: string, priority = 5) =>
    api
      .post<{ job_id: string; celery_task_id: string }>('/jobs/orchestrate', {
        story_id: storyId,
        directive,
        priority,
      })
      .then((r) => r.data),

  analyzeChapter: (chapterId: string) =>
    api.post<{ job_id: string }>(`/jobs/analyze-chapter/${chapterId}`).then((r) => r.data),

  extractEntities: (chapterId: string) =>
    api.post<{ job_id: string }>(`/jobs/extract-entities/${chapterId}`).then((r) => r.data),

  checkConsistency: (storyId: string) =>
    api.post<{ job_id: string }>(`/jobs/check-consistency/${storyId}`).then((r) => r.data),
}
