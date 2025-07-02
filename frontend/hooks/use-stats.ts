import { useQuery } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'

/**
 * Хук для получения глобальной статистики
 */
export function useGlobalStats() {
  return useQuery({
    queryKey: createQueryKey.globalStats(),
    queryFn: () => api.getGlobalStats(),
    staleTime: 1 * 60 * 1000, // 1 минута
    refetchInterval: 2 * 60 * 1000, // Обновляем каждые 2 минуты
  })
}

/**
 * Хук для получения статистики дашборда
 */
export function useDashboardStats() {
  return useQuery({
    queryKey: createQueryKey.dashboardStats(),
    queryFn: () => api.getDashboardStats(),
    staleTime: 30 * 1000, // 30 секунд
    refetchInterval: 60 * 1000, // Обновляем каждую минуту
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