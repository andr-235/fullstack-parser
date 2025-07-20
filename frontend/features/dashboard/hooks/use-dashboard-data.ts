import { useQuery } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import { useGlobalStats, useDashboardStats } from '@/hooks/use-stats'
import type {
  GlobalStats,
  DashboardStats,
  VKGroupResponse,
  KeywordResponse,
  VKCommentResponse,
} from '@/types/api'

/**
 * Хук для получения данных для графиков активности
 */
export function useActivityData(timeRange: string = '7d') {
  return useQuery({
    queryKey: createQueryKey.activityData(timeRange),
    queryFn: () => api.getActivityData({ timeRange }),
    staleTime: 5 * 60 * 1000, // 5 минут
    enabled: !!timeRange,
  })
}

/**
 * Хук для получения топ групп
 */
export function useTopGroups(limit: number = 10) {
  return useQuery({
    queryKey: createQueryKey.topGroups(limit),
    queryFn: () => api.getTopGroups({ limit }),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

/**
 * Хук для получения топ ключевых слов
 */
export function useTopKeywords(limit: number = 10) {
  return useQuery({
    queryKey: createQueryKey.topKeywords(limit),
    queryFn: () => api.getTopKeywords({ limit }),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

/**
 * Хук для получения последних комментариев
 */
export function useRecentComments(limit: number = 20) {
  return useQuery({
    queryKey: createQueryKey.recentComments(limit),
    queryFn: () => api.getRecentComments({ limit }),
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

/**
 * Хук для получения статистики по группам
 */
export function useGroupStats(groupId: number) {
  return useQuery({
    queryKey: createQueryKey.groupStats(groupId),
    queryFn: () => api.getGroupStats(groupId),
    staleTime: 15 * 60 * 1000, // 15 минут
    enabled: !!groupId,
  })
}

/**
 * Хук для получения статуса системы
 */
export function useSystemStatus() {
  return useQuery({
    queryKey: createQueryKey.systemStatus(),
    queryFn: () => api.getSystemStatus(),
    staleTime: 30 * 1000, // 30 секунд
    refetchInterval: 60 * 1000, // Обновление каждую минуту
  })
}

/**
 * Хук для получения прогресса парсинга
 */
export function useParsingProgress() {
  return useQuery({
    queryKey: createQueryKey.parsingProgress(),
    queryFn: () => api.getParsingProgress(),
    staleTime: 10 * 1000, // 10 секунд
    refetchInterval: 30 * 1000, // Обновление каждые 30 секунд
  })
}

/**
 * Хук для получения последней активности
 */
export function useRecentActivity(limit: number = 10) {
  return useQuery({
    queryKey: createQueryKey.recentActivity(limit),
    queryFn: () => api.getRecentActivity({ limit }),
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

/**
 * Хук для получения данных для дашборда с кэшированием
 */
export function useDashboardData() {
  const globalStats = useGlobalStats()
  const dashboardStats = useDashboardStats()
  const activityData = useActivityData('7d')
  const topGroups = useTopGroups(5)
  const topKeywords = useTopKeywords(5)
  const recentComments = useRecentComments(10)
  const systemStatus = useSystemStatus()
  const parsingProgress = useParsingProgress()
  const recentActivity = useRecentActivity(5)

  const isLoading =
    globalStats.isLoading ||
    dashboardStats.isLoading ||
    activityData.isLoading ||
    topGroups.isLoading ||
    topKeywords.isLoading ||
    recentComments.isLoading ||
    systemStatus.isLoading ||
    parsingProgress.isLoading ||
    recentActivity.isLoading

  const error =
    globalStats.error ||
    dashboardStats.error ||
    activityData.error ||
    topGroups.error ||
    topKeywords.error ||
    recentComments.error ||
    systemStatus.error ||
    parsingProgress.error ||
    recentActivity.error

  return {
    data: {
      globalStats: globalStats.data,
      dashboardStats: dashboardStats.data,
      activityData: activityData.data,
      topGroups: topGroups.data,
      topKeywords: topKeywords.data,
      recentComments: recentComments.data,
      systemStatus: systemStatus.data,
      parsingProgress: parsingProgress.data,
      recentActivity: recentActivity.data,
    },
    isLoading,
    error,
    refetch: () => {
      globalStats.refetch()
      dashboardStats.refetch()
      activityData.refetch()
      topGroups.refetch()
      topKeywords.refetch()
      recentComments.refetch()
      systemStatus.refetch()
      parsingProgress.refetch()
      recentActivity.refetch()
    },
  }
}
