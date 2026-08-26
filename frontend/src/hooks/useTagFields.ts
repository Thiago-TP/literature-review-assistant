import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fieldsApi } from '../api/fields'

export function useTagFields(projectId: number) {
  return useQuery({ queryKey: ['projects', projectId, 'fields'], queryFn: () => fieldsApi.list(projectId) })
}

export function useFieldMutations(projectId: number) {
  const queryClient = useQueryClient()
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'fields'] })
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'dashboard'] })
  }

  const addField = useMutation({
    mutationFn: (name: string) => fieldsApi.create(projectId, name),
    onSuccess: invalidate,
  })
  const renameField = useMutation({
    mutationFn: ({ fieldId, name }: { fieldId: number; name: string }) =>
      fieldsApi.rename(projectId, fieldId, name),
    onSuccess: invalidate,
  })
  const deleteField = useMutation({
    mutationFn: (fieldId: number) => fieldsApi.remove(projectId, fieldId),
    onSuccess: invalidate,
  })
  const addOption = useMutation({
    mutationFn: ({
      fieldId,
      value,
      parentOptionId,
      weight,
    }: {
      fieldId: number
      value: string
      parentOptionId?: number
      weight?: number
    }) => fieldsApi.addOption(projectId, fieldId, value, parentOptionId, weight),
    onSuccess: invalidate,
  })
  const updateOption = useMutation({
    mutationFn: ({
      fieldId,
      optionId,
      value,
      weight,
    }: {
      fieldId: number
      optionId: number
      value?: string
      weight?: number
    }) => fieldsApi.updateOption(projectId, fieldId, optionId, { value, weight }),
    onSuccess: invalidate,
  })
  const deleteOption = useMutation({
    mutationFn: ({ fieldId, optionId }: { fieldId: number; optionId: number }) =>
      fieldsApi.removeOption(projectId, fieldId, optionId),
    onSuccess: invalidate,
  })

  return { addField, renameField, deleteField, addOption, updateOption, deleteOption }
}
