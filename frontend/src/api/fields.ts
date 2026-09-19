import { api } from './client'
import type { TagField, TagOption } from '../types'

export const fieldsApi = {
  list: (projectId: number) => api.get<TagField[]>(`/projects/${projectId}/fields`),
  create: (projectId: number, name: string) =>
    api.post<TagField>(`/projects/${projectId}/fields`, { name }),
  rename: (projectId: number, fieldId: number, name: string) =>
    api.patch<TagField>(`/projects/${projectId}/fields/${fieldId}`, { name }),
  // Separate from `rename` because a protected field can be described but not
  // renamed, so the two cannot share a request.
  describe: (projectId: number, fieldId: number, description: string) =>
    api.patch<TagField>(`/projects/${projectId}/fields/${fieldId}`, { description }),
  remove: (projectId: number, fieldId: number) =>
    api.delete<void>(`/projects/${projectId}/fields/${fieldId}`),
  addOption: (projectId: number, fieldId: number, value: string, parentOptionId?: number, weight?: number) =>
    api.post<TagOption>(`/projects/${projectId}/fields/${fieldId}/options`, {
      value,
      parent_option_id: parentOptionId ?? null,
      weight: weight ?? 0,
    }),
  updateOption: (
    projectId: number,
    fieldId: number,
    optionId: number,
    payload: { value?: string; weight?: number; description?: string }
  ) => api.patch<TagOption>(`/projects/${projectId}/fields/${fieldId}/options/${optionId}`, payload),
  removeOption: (projectId: number, fieldId: number, optionId: number) =>
    api.delete(`/projects/${projectId}/fields/${fieldId}/options/${optionId}`),
}
