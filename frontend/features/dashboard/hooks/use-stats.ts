import { useQuery } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import type { DashboardStats, GlobalStats } from '@/types/api'

/**
 * Хук для получения общей статистики для дашборда
 */
export function useDashboardStats() {
  return useQuery<DashboardStats>({
    queryKey: createQueryKey.dashboardStats(),
    queryFn: () => api.getDashboardStats(),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

/**
 * Хук для получения глобальной статистики
 */
export function useGlobalStats() {
  return useQuery<GlobalStats>({
    queryKey: createQueryKey.globalStats(),
    queryFn: () => api.getGlobalStats(),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

/**
 * Хук для проверки статуса API
 */
export function useAPIHealth() {
  return useQuery({
    queryKey: ['api', 'health'],
    queryFn: () => api.healthCheck(),
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
    retry: 3,
  })
}
