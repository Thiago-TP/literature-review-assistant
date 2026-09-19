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
    // Fields and tags are half the review plan: describing one fills an item,
    // and adding one adds an item to fill. Both move the counts the plan page
    // and the project list badge are drawn from.
    queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'plan'] })
    // `exact` so this hits only the project list, not every key beneath it.
    queryClient.invalidateQueries({ queryKey: ['projects'], exact: true })
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
  const describeField = useMutation({
    mutationFn: ({ fieldId, description }: { fieldId: number; description: string }) =>
      fieldsApi.describe(projectId, fieldId, description),
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
      description,
    }: {
      fieldId: number
      optionId: number
      value?: string
      weight?: number
      description?: string
    }) => fieldsApi.updateOption(projectId, fieldId, optionId, { value, weight, description }),
    onSuccess: invalidate,
  })
  const deleteOption = useMutation({
    mutationFn: ({ fieldId, optionId }: { fieldId: number; optionId: number }) =>
      fieldsApi.removeOption(projectId, fieldId, optionId),
    onSuccess: invalidate,
  })

  return {
    addField,
    renameField,
    describeField,
    deleteField,
    addOption,
    updateOption,
    deleteOption,
  }
}
