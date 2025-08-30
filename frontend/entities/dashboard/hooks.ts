import { useState, useEffect, useMemo } from 'react'
import { apiClient } from '@/shared/lib'
import {
  GlobalStats,
  DashboardStats,
  DashboardMetrics,
  ActivitySummary,
  GroupsResponse,
  KeywordsResponse,
} from './types'

export const useGlobalStats = () => {
  const [stats, setStats] = useState<GlobalStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const data: GlobalStats = await apiClient.getGlobalStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch global stats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

export const useDashboardStats = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const data: DashboardStats = await apiClient.getDashboardStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard stats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

export const useGroups = (params?: {
  page?: number
  size?: number
  is_active?: boolean
  active_only?: boolean
  search?: string
}) => {
  const [groups, setGroups] = useState<GroupsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchGroups = async () => {
    setLoading(true)
    setError(null)
    try {
      // Convert old params to new API format
      const apiParams: any = {}

      if (params?.active_only !== undefined) {
        apiParams.active_only = params.active_only
      } else if (params?.is_active !== undefined) {
        apiParams.active_only = params.is_active
      }

      if (params?.search) {
        apiParams.search = params.search
      }

      const data: GroupsResponse = await apiClient.getGroups(apiParams)
      setGroups(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch groups')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGroups()
  }, [params?.page, params?.size, params?.is_active, params?.active_only, params?.search])

  return {
    groups,
    loading,
    error,
    refetch: fetchGroups,
  }
}

export const useKeywords = (params?: { page?: number; size?: number; is_active?: boolean }) => {
  const [keywords, setKeywords] = useState<KeywordsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchKeywords = async () => {
    setLoading(true)
    setError(null)
    try {
      const data: KeywordsResponse = await apiClient.getKeywords(params)
      setKeywords(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keywords')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKeywords()
  }, [params?.page, params?.size, params?.is_active])

  return {
    keywords,
    loading,
    error,
    refetch: fetchKeywords,
  }
}

// Хук для вычисляемых метрик dashboard
export const useDashboardMetrics = () => {
  const { stats: dashboardStats, loading: dashboardLoading } = useDashboardStats()
  const { stats: globalStats, loading: globalLoading } = useGlobalStats()

  const metrics = useMemo((): DashboardMetrics | null => {
    if (!dashboardStats || !globalStats) return null

    const matchRate =
      dashboardStats.today_comments > 0
        ? (dashboardStats.today_matches / dashboardStats.today_comments) * 100
        : 0

    return {
      today_comments: dashboardStats.today_comments,
      today_matches: dashboardStats.today_matches,
      week_comments: dashboardStats.week_comments,
      week_matches: dashboardStats.week_matches,
      match_rate: matchRate,
    }
  }, [dashboardStats, globalStats])

  return {
    metrics,
    loading: dashboardLoading || globalLoading,
  }
}

// Хук для сводки активности
export const useActivitySummary = () => {
  const { stats: dashboardStats, loading: dashboardLoading } = useDashboardStats()
  const { stats: globalStats, loading: globalLoading } = useGlobalStats()

  const summary = useMemo((): ActivitySummary | null => {
    if (!dashboardStats || !globalStats) return null

    return {
      total_today: dashboardStats.today_comments,
      matches_today: dashboardStats.today_matches,
      active_groups: globalStats.active_groups,
      active_keywords: globalStats.active_keywords,
    }
  }, [dashboardStats, globalStats])

  return {
    summary,
    loading: dashboardLoading || globalLoading,
  }
}

// Хук для трендов (сравнение с предыдущими периодами)
export const useTrends = () => {
  const { stats: dashboardStats, loading } = useDashboardStats()

  const trends = useMemo(() => {
    if (!dashboardStats) return null

    // Рассчитываем дневные тренды (предполагая что week_* данные за 7 дней)
    const dailyAverage = dashboardStats.week_comments / 7
    const todayVsAverage = dashboardStats.today_comments - dailyAverage

    const dailyMatchAverage = dashboardStats.week_matches / 7
    const todayMatchVsAverage = dashboardStats.today_matches - dailyMatchAverage

    return {
      comments_trend: {
        today_vs_average: todayVsAverage,
        daily_average: dailyAverage,
        is_positive: todayVsAverage > 0,
      },
      matches_trend: {
        today_vs_average: todayMatchVsAverage,
        daily_average: dailyMatchAverage,
        is_positive: todayMatchVsAverage > 0,
      },
    }
  }, [dashboardStats])

  return {
    trends,
    loading,
  }
}
