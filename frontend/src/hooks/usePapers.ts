import { useEffect } from 'react'
import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { papersApi, type PaperCreatePayload } from '../api/papers'
import type { PaperListItem } from '../types'

/**
 * A fetched paper stays usable for this long without a refetch. Mutations
 * invalidate it explicitly, so this only affects revisiting a paper you have
 * already seen -- which is exactly what stepping back and forth does.
 */
const PAPER_STALE_TIME_MS = 30_000

export function usePapers(projectId: number) {
  return useQuery({ queryKey: ['projects', projectId, 'papers'], queryFn: () => papersApi.list(projectId) })
}

export function usePaper(projectId: number, paperId: number | null) {
  return useQuery({
    queryKey: ['projects', projectId, 'papers', paperId],
    queryFn: () => papersApi.get(projectId, paperId as number),
    enabled: paperId !== null,
    // Keep the paper already on screen while the next one loads. Without this
    // every step through the list unmounts the whole workspace for the length
    // of one request, which reads as a flicker when stepping quickly.
    placeholderData: keepPreviousData,
    staleTime: PAPER_STALE_TIME_MS,
  })
}

/**
 * Warms the cache for the papers on either side of `index`, so the next step
 * in either direction renders from cache instead of waiting on a request.
 */
export function usePrefetchAdjacentPapers(
  projectId: number,
  papers: PaperListItem[] | undefined,
  index: number
) {
  const queryClient = useQueryClient()
  useEffect(() => {
    if (!papers || index < 0) return
    for (const neighbour of [papers[index - 1], papers[index + 1]]) {
      if (!neighbour) continue
      const id = neighbour.id
      queryClient.prefetchQuery({
        queryKey: ['projects', projectId, 'papers', id],
        queryFn: () => papersApi.get(projectId, id),
        staleTime: PAPER_STALE_TIME_MS,
      })
    }
  }, [queryClient, projectId, papers, index])
}

function invalidatePaperQueries(queryClient: ReturnType<typeof useQueryClient>, projectId: number, paperId: number) {
  queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
  queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers', paperId] })
  queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'dashboard'] })
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
    onSuccess: (_data, variables) => invalidatePaperQueries(queryClient, projectId, variables.paperId),
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
    onSuccess: (_data, variables) => invalidatePaperQueries(queryClient, projectId, variables.paperId),
  })
}

export function useRating(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ paperId, rating }: { paperId: number; rating: number | null }) =>
      rating === null
        ? papersApi.clearRating(projectId, paperId)
        : papersApi.setRating(projectId, paperId, rating),
    onSuccess: (_data, variables) => invalidatePaperQueries(queryClient, projectId, variables.paperId),
  })
}

export function useCreatePaper(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: PaperCreatePayload) => papersApi.create(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'dashboard'] })
    },
  })
}

export function useDeletePaper(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (paperId: number) => papersApi.remove(projectId, paperId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'dashboard'] })
    },
  })
}
