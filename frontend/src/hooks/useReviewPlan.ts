import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { reviewPlanApi, type ReviewPlanPayload } from '../api/reviewPlan'

export function useReviewPlan(projectId: number) {
  return useQuery({
    queryKey: ['projects', projectId, 'plan'],
    queryFn: () => reviewPlanApi.get(projectId),
  })
}

export function useUpdateReviewPlan(projectId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: ReviewPlanPayload) => reviewPlanApi.update(projectId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'plan'] })
      // The project list badges an unfinished plan, so its copy of the counts
      // has to go too.
      queryClient.invalidateQueries({ queryKey: ['projects'], exact: true })
      // `exact` for the same reason as in useProjects: ['projects', id] is a
      // prefix of every paper, field and dashboard key for this project.
      queryClient.invalidateQueries({ queryKey: ['projects', projectId], exact: true })
    },
  })
}
