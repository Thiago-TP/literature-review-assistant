import { useCallback, useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../api/projects'

export function useProjects() {
  return useQuery({ queryKey: ['projects'], queryFn: projectsApi.list })
}

export function useProject(projectId: number) {
  return useQuery({ queryKey: ['projects', projectId], queryFn: () => projectsApi.get(projectId) })
}

export function useCreateProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => projectsApi.create(name),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  })
}

export function useRenameProject(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (name: string) => projectsApi.rename(projectId, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId] })
    },
  })
}

export function useDeleteProject() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (projectId: number) => projectsApi.remove(projectId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['projects'] }),
  })
}

export function useSetLastViewed(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (paperId: number) => projectsApi.setLastViewed(projectId, paperId),
    // `exact` matters: ['projects', projectId] is a prefix of every paper,
    // dashboard and paper-list key for this project, so a loose invalidation
    // here would throw away the whole project's cache on each bookmark write.
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['projects', projectId], exact: true }),
  })
}

/** Rapid navigation coalesces into one bookmark write after this long. */
const LAST_VIEWED_DEBOUNCE_MS = 400

/**
 * Debounced counterpart to `useSetLastViewed`, for stepping through papers.
 *
 * The last-viewed id is a "where was I?" bookmark that is only read back when
 * the workspace next mounts, so a round trip per keypress buys nothing -- and
 * racing writes can settle on whichever request happened to answer last rather
 * than on the paper the user stopped at. Coalesce a burst of navigation into a
 * single write, and flush a pending one on unmount so leaving straight away
 * still records where you stopped.
 */
export function useRememberLastViewed(projectId: number) {
  const queryClient = useQueryClient()
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const pendingRef = useRef<number | null>(null)

  const flush = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    const paperId = pendingRef.current
    pendingRef.current = null
    if (paperId === null) return
    projectsApi
      .setLastViewed(projectId, paperId)
      .then(() => queryClient.invalidateQueries({ queryKey: ['projects', projectId], exact: true }))
      // A failed bookmark write is not worth surfacing: the only consequence
      // is that the next visit starts on the first paper instead.
      .catch(() => undefined)
  }, [projectId, queryClient])

  useEffect(() => flush, [flush])

  return useCallback(
    (paperId: number) => {
      pendingRef.current = paperId
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(flush, LAST_VIEWED_DEBOUNCE_MS)
    },
    [flush]
  )
}
