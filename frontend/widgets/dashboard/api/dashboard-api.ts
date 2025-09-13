import { apiClient } from '@/shared/api/client'

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
  const response = await apiClient.get('/api/v1/metrics/dashboard')
  return response.data
}

/**
 * Получить метрики комментариев
 */
export const getCommentsMetrics = async (): Promise<CommentsMetricsResponse> => {
  const response = await apiClient.get('/api/v1/comments/metrics')
  return response.data
}

/**
 * Получить метрики групп
 */
export const getGroupsMetrics = async (): Promise<GroupsMetricsResponse> => {
  const response = await apiClient.get('/api/v1/groups/metrics')
  return response.data
}

/**
 * Получить метрики ключевых слов
 */
export const getKeywordsMetrics = async (): Promise<KeywordsMetricsResponse> => {
  const response = await apiClient.get('/api/v1/keywords/metrics')
  return response.data
}
