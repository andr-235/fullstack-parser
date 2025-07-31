import { useQuery } from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type { DashboardStats, GlobalStats, ParserState } from '@/types/api'

// Хук для получения статистики активности
export function useActivityData(timeRange: string = '7d') {
  return useQuery({
    queryKey: ['activity', timeRange],
    queryFn: () => api.get<DashboardStats>(`/stats/dashboard`),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для получения топ групп
export function useTopGroups(limit: number = 5) {
  return useQuery({
    queryKey: ['top-groups', limit],
    queryFn: () => api.get<any[]>(`/stats/dashboard`),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

// Хук для получения топ ключевых слов
export function useTopKeywords(limit: number = 5) {
  return useQuery({
    queryKey: ['top-keywords', limit],
    queryFn: () => api.get<any[]>(`/stats/dashboard`),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

// Хук для получения последних комментариев
export function useRecentComments(limit: number = 20) {
  return useQuery({
    queryKey: ['recent-comments', limit],
    queryFn: () => api.get<any[]>(`/stats/dashboard`),
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

// Хук для получения статуса системы
export function useSystemStatus() {
  return useQuery({
    queryKey: ['system-status'],
    queryFn: () => api.get<any>('/health/'),
    refetchInterval: 30 * 1000, // 30 секунд
    staleTime: 10 * 1000, // 10 секунд
  })
}

// Хук для получения прогресса парсинга
export function useParsingProgress() {
  return useQuery({
    queryKey: ['parser-progress'],
    queryFn: () => api.get<ParserState>('/parser/state'),
    refetchInterval: 5 * 1000, // 5 секунд
    staleTime: 1 * 1000, // 1 секунда
  })
}

// Хук для получения последней активности
export function useRecentActivity(limit: number = 10) {
  return useQuery({
    queryKey: ['recent-activity', limit],
    queryFn: () => api.get<any[]>(`/stats/dashboard`),
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

// Хук для получения всех данных дашборда
export function useDashboardData() {
  const activityData = useActivityData()
  const topGroups = useTopGroups(5)
  const topKeywords = useTopKeywords(5)
  const recentComments = useRecentComments(5)
  const systemStatus = useSystemStatus()
  const parsingProgress = useParsingProgress()

  return {
    activityData,
    topGroups,
    topKeywords,
    recentComments,
    systemStatus,
    parsingProgress,
    isLoading:
      activityData.isLoading ||
      topGroups.isLoading ||
      topKeywords.isLoading ||
      recentComments.isLoading ||
      systemStatus.isLoading ||
      parsingProgress.isLoading,
    error:
      activityData.error ||
      topGroups.error ||
      topKeywords.error ||
      recentComments.error ||
      systemStatus.error ||
      parsingProgress.error,
  }
}
