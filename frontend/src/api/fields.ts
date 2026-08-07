import { api } from './client'
import type { TagField } from '../types'

export const fieldsApi = {
  list: (projectId: number) => api.get<TagField[]>(`/projects/${projectId}/fields`),
  create: (projectId: number, name: string) =>
    api.post<TagField>(`/projects/${projectId}/fields`, { name }),
  rename: (projectId: number, fieldId: number, name: string) =>
    api.patch<TagField>(`/projects/${projectId}/fields/${fieldId}`, { name }),
  remove: (projectId: number, fieldId: number) =>
    api.delete<void>(`/projects/${projectId}/fields/${fieldId}`),
  addOption: (projectId: number, fieldId: number, value: string, parentOptionId?: number) =>
    api.post(`/projects/${projectId}/fields/${fieldId}/options`, {
      value,
      parent_option_id: parentOptionId ?? null,
    }),
  renameOption: (projectId: number, fieldId: number, optionId: number, value: string) =>
    api.patch(`/projects/${projectId}/fields/${fieldId}/options/${optionId}`, { value }),
  removeOption: (projectId: number, fieldId: number, optionId: number) =>
    api.delete(`/projects/${projectId}/fields/${fieldId}/options/${optionId}`),
}
