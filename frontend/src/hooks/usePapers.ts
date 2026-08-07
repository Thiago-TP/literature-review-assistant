import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { papersApi, type PaperCreatePayload } from '../api/papers'

export function usePapers(projectId: number) {
  return useQuery({ queryKey: ['projects', projectId, 'papers'], queryFn: () => papersApi.list(projectId) })
}

export function usePaper(projectId: number, paperId: number | null) {
  return useQuery({
    queryKey: ['projects', projectId, 'papers', paperId],
    queryFn: () => papersApi.get(projectId, paperId as number),
    enabled: paperId !== null,
  })
}

export function useUpdatePaper(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      paperId,
      payload,
    }: {
      paperId: number
      payload: { notes?: string; tags?: Record<number, number[]> }
    }) => papersApi.update(projectId, paperId, payload),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', variables.paperId] })
    },
  })
}

export function useToggleTag(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    // Each call only ever asserts one option's assignment state -- never a
    // client-computed full list -- so clicking a topic and a subtopic in
    // quick succession can't have one click's request clobber the other's.
    mutationFn: ({ paperId, optionId, assign }: { paperId: number; optionId: number; assign: boolean }) =>
      assign
        ? papersApi.assignTag(projectId, paperId, optionId)
        : papersApi.unassignTag(projectId, paperId, optionId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', variables.paperId] })
    },
  })
}

export function useCreatePaper(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: PaperCreatePayload) => papersApi.create(projectId, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] }),
  })
}

export function useDeletePaper(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (paperId: number) => papersApi.remove(projectId, paperId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] }),
  })
}
