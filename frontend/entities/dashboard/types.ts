import { ID } from '@/shared/types'

// Типы соответствующие backend схемам статистики
export interface GlobalStats {
  total_groups: number
  active_groups: number
  total_keywords: number
  active_keywords: number
  total_comments: number
  comments_with_keywords: number
  last_parse_time?: string
}

export interface DashboardTopItem {
  name: string
  count: number
}

export interface RecentActivityItem {
  id: number
  type: string
  message: string
  timestamp: string
}

export interface DashboardStats {
  today_comments: number
  today_matches: number
  week_comments: number
  week_matches: number
  top_groups: DashboardTopItem[]
  top_keywords: DashboardTopItem[]
  recent_activity: RecentActivityItem[]
}

// Дополнительные типы для статистики
export interface DashboardMetrics {
  today_comments: number
  today_matches: number
  week_comments: number
  week_matches: number
  match_rate: number
}

export interface ActivitySummary {
  total_today: number
  matches_today: number
  active_groups: number
  active_keywords: number
}

// Import types from respective entities
import { VKGroup } from '../groups/types'
import { Keyword } from '../keywords/types'

// Re-export for convenience
export type { VKGroup, Keyword }

// Response types - import from respective entities
import { GroupsResponse } from '../groups/types'
import { KeywordsResponse } from '../keywords/types'

// Re-export for convenience
export type { GroupsResponse, KeywordsResponse }
