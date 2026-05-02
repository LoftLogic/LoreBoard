import { api } from './client'
import type { FeedbackRequest } from '@/types/story'

export const feedbackApi = {
  submit: (body: FeedbackRequest) =>
    api.post<{ feedback_id: string }>('/feedback', body).then((r) => r.data),

  forceCalibration: (runId: string) =>
    api.post(`/feedback/force-calibration/${runId}`).then((r) => r.data),

  getCalibration: (agentType: string) =>
    api.get(`/feedback/calibration/${agentType}`).then((r) => r.data),
}
