import { useQuery } from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type { DashboardStats, GlobalStats } from '@/types/api'

// Хук для получения статистики дашборда
export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => api.get<DashboardStats>('/stats/dashboard'),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для получения глобальной статистики
export function useGlobalStats() {
  return useQuery({
    queryKey: ['global-stats'],
    queryFn: () => api.get<GlobalStats>('/stats/global'),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

// Хук для проверки здоровья API
export function useAPIHealth() {
  return useQuery({
    queryKey: ['api-health'],
    queryFn: () => api.get<any>('/health/'),
    refetchInterval: 30 * 1000, // 30 секунд
    staleTime: 10 * 1000, // 10 секунд
  })
}
