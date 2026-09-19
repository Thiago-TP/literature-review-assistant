import { api } from './client'
import type { DashboardStats } from '../types'

export const dashboardApi = {
  get: (projectId: number) => api.get<DashboardStats>(`/projects/${projectId}/dashboard`),
}
