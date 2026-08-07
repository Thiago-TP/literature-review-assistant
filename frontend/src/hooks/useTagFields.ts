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
    mutationFn: ({ fieldId, value, parentOptionId }: { fieldId: number; value: string; parentOptionId?: number }) =>
      fieldsApi.addOption(projectId, fieldId, value, parentOptionId),
    onSuccess: invalidate,
  })
  const renameOption = useMutation({
    mutationFn: ({ fieldId, optionId, value }: { fieldId: number; optionId: number; value: string }) =>
      fieldsApi.renameOption(projectId, fieldId, optionId, value),
    onSuccess: invalidate,
  })
  const deleteOption = useMutation({
    mutationFn: ({ fieldId, optionId }: { fieldId: number; optionId: number }) =>
      fieldsApi.removeOption(projectId, fieldId, optionId),
    onSuccess: invalidate,
  })

  return { addField, renameField, deleteField, addOption, renameOption, deleteOption }
}
