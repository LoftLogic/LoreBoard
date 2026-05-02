import { api } from './client'
import type { Story } from '@/types/story'

export const storiesApi = {
  create: (title: string, meta: Record<string, unknown> = {}) =>
    api.post<Story>('/stories', { title, meta }).then((r) => r.data),

  get: (storyId: string) =>
    api.get<Story>(`/stories/${storyId}`).then((r) => r.data),

  flags: (storyId: string, resolved = false) =>
    api.get(`/stories/${storyId}/flags`, { params: { resolved } }).then((r) => r.data),
}
