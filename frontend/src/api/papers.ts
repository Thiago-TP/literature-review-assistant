import { api } from './client'
import type {
  HighlightField,
  PaperCreateResult,
  PaperDetail,
  PaperListItem,
  PaperSource,
} from '../types'

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
  setRating: (projectId: number, paperId: number, rating: number) =>
    api.put<PaperDetail>(`/projects/${projectId}/papers/${paperId}/rating`, { rating }),
  clearRating: (projectId: number, paperId: number) =>
    api.delete<PaperDetail>(`/projects/${projectId}/papers/${paperId}/rating`),
  addHighlight: (
    projectId: number,
    paperId: number,
    field: HighlightField,
    start: number,
    end: number
  ) =>
    api.post<PaperDetail>(`/projects/${projectId}/papers/${paperId}/highlights`, {
      field,
      start,
      end,
    }),
  removeHighlight: (projectId: number, paperId: number, highlightId: string) =>
    api.delete<PaperDetail>(
      `/projects/${projectId}/papers/${paperId}/highlights/${highlightId}`
    ),
  clearHighlights: (projectId: number, paperId: number) =>
    api.delete<PaperDetail>(`/projects/${projectId}/papers/${paperId}/highlights`),
}
