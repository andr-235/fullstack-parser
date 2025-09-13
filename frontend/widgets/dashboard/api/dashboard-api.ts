import { apiClient } from '@/shared/api/client'
import { getRoutePath, DASHBOARD_ROUTES, COMMENTS_ROUTES, GROUPS_ROUTES, KEYWORDS_ROUTES } from '@/shared/config/routes'

export interface DashboardMetricsResponse {
  comments: {
    total: number
    growth_percentage: number
    trend: string
  }
  groups: {
    active: number
    growth_percentage: number
    trend: string
  }
  keywords: {
    total: number
    growth_percentage: number
    trend: string
  }
  parsers: {
    active: number
    growth_percentage: number
    trend: string
  }
}

export interface CommentsMetricsResponse {
  total_comments: number
  growth_percentage: number
  trend: string
}

export interface GroupsMetricsResponse {
  active_groups: number
  growth_percentage: number
  trend: string
}

export interface KeywordsMetricsResponse {
  total_keywords: number
  active_keywords: number
  growth_percentage: number
  trend: string
}

/**
  * Получить общие метрики дашборда
  */
export const getDashboardMetrics = async (): Promise<DashboardMetricsResponse> => {
  const response = await apiClient.get(getRoutePath(DASHBOARD_ROUTES.METRICS))
  return response.data
}

/**
  * Получить метрики комментариев
  */
export const getCommentsMetrics = async (): Promise<CommentsMetricsResponse> => {
  const response = await apiClient.get(getRoutePath(COMMENTS_ROUTES.METRICS))
  return response.data
}

/**
  * Получить метрики групп
  */
export const getGroupsMetrics = async (): Promise<GroupsMetricsResponse> => {
  const response = await apiClient.get(getRoutePath(GROUPS_ROUTES.METRICS))
  return response.data
}

/**
  * Получить метрики ключевых слов
  */
export const getKeywordsMetrics = async (): Promise<KeywordsMetricsResponse> => {
  const response = await apiClient.get(getRoutePath(KEYWORDS_ROUTES.METRICS))
  return response.data
}
