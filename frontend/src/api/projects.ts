import { api } from './client'
import type { Project } from '../types'

export const projectsApi = {
  list: () => api.get<Project[]>('/projects'),
  get: (id: number) => api.get<Project>(`/projects/${id}`),
  create: (name: string) => api.post<Project>('/projects', { name }),
  rename: (id: number, name: string) => api.patch<Project>(`/projects/${id}`, { name }),
  remove: (id: number) => api.delete<void>(`/projects/${id}`),
  setLastViewed: (id: number, paperId: number) =>
    api.patch<Project>(`/projects/${id}/last-viewed`, { paper_id: paperId }),
}
