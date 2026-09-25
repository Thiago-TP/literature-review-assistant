import { api } from './client'
import type { ImportCommitResponse, ImportPreviewResponse, ImportPreviewRow, LookupCandidate } from '../types'

export const importApi = {
  preview: (projectId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.postForm<ImportPreviewResponse>(`/projects/${projectId}/import/preview`, form)
  },
  commit: (projectId: number, rows: ImportPreviewRow[], actions: Record<number, 'add' | 'skip'>) =>
    api.post<ImportCommitResponse>(`/projects/${projectId}/import/commit`, { rows, actions }),
  lookupByDoi: (projectId: number, doi: string) =>
    api.post<{ candidate: LookupCandidate }>(`/projects/${projectId}/papers/lookup/doi`, { doi }),
  lookupByTitle: (projectId: number, title: string) =>
    api.post<{ candidates: LookupCandidate[] }>(`/projects/${projectId}/papers/lookup/title`, { title }),
}
