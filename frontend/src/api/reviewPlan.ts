import { api } from './client'
import type { PlanSection, ReviewPlan } from '../types'

/** Only the sections being saved are sent; the rest are left as they are. */
export type ReviewPlanPayload = Partial<Record<PlanSection, string>>

export const reviewPlanApi = {
  get: (projectId: number) => api.get<ReviewPlan>(`/projects/${projectId}/plan`),
  update: (projectId: number, payload: ReviewPlanPayload) =>
    api.patch<ReviewPlan>(`/projects/${projectId}/plan`, payload),
}
