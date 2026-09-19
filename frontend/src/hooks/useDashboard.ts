import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../api/dashboard'

export function useDashboard(projectId: number) {
  return useQuery({ queryKey: ['projects', projectId, 'dashboard'], queryFn: () => dashboardApi.get(projectId) })
}
