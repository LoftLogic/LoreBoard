import { api } from './client'
import type { Chapter, ChapterOverrides } from '@/types/story'

export const chaptersApi = {
  create: (payload: { story_id: string; order: number; title?: string; content?: string }) =>
    api.post<Chapter>('/chapters', payload).then((r) => r.data),

  updateContent: (chapterId: string, content: string) =>
    api
      .patch<{ status: string; analysis_state: string }>(`/chapters/${chapterId}/content`, { content })
      .then((r) => r.data),

  setOverride: (chapterId: string, key: string, value: string) =>
    api.post(`/chapters/${chapterId}/overrides`, { key, value }).then((r) => r.data),

  getOverrides: (chapterId: string) =>
    api.get<ChapterOverrides>(`/chapters/${chapterId}/overrides`).then((r) => r.data),
}
