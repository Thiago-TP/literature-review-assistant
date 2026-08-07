import { api } from './client'
import type { PaperCreateResult, PaperDetail, PaperListItem, PaperSource } from '../types'

export interface PaperCreatePayload {
  title: string
  abstract?: string | null
  doi?: string | null
  authors?: string | null
  year?: number | null
  source_title?: string | null
  source?: PaperSource
  raw_metadata?: Record<string, unknown> | null
  force?: boolean
}

export const papersApi = {
  list: (projectId: number) => api.get<PaperListItem[]>(`/projects/${projectId}/papers`),
  get: (projectId: number, paperId: number) =>
    api.get<PaperDetail>(`/projects/${projectId}/papers/${paperId}`),
  update: (
    projectId: number,
    paperId: number,
    payload: { notes?: string; tags?: Record<number, number[]> }
  ) => api.patch<PaperDetail>(`/projects/${projectId}/papers/${paperId}`, payload),
  remove: (projectId: number, paperId: number) =>
    api.delete<void>(`/projects/${projectId}/papers/${paperId}`),
  create: (projectId: number, payload: PaperCreatePayload) =>
    api.post<PaperCreateResult>(`/projects/${projectId}/papers`, payload),
  assignTag: (projectId: number, paperId: number, optionId: number) =>
    api.post<PaperDetail>(`/projects/${projectId}/papers/${paperId}/tags/${optionId}`),
  unassignTag: (projectId: number, paperId: number, optionId: number) =>
    api.delete<PaperDetail>(`/projects/${projectId}/papers/${paperId}/tags/${optionId}`),
}
