export interface GlobalStats {
  total_comments: number
  total_matches: number
  comments_with_keywords: number
  active_groups: number
  active_keywords: number
  total_groups: number
  total_keywords: number
}

export interface DashboardStats {
  today_comments: number
  today_matches: number
  week_comments: number
  week_matches: number
  recent_activity: RecentActivityItem[]
  top_groups: DashboardTopItem[]
  top_keywords: DashboardTopItem[]
}

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

export interface Group {
  id: number
  name: string
  screen_name: string
  is_active: boolean
  members_count?: number
  description?: string
  created_at: string
  updated_at: string
}

export interface GroupsResponse {
  items: Group[]
  total: number
  page: number
  size: number
  pages: number
}

export interface Keyword {
  id: number
  word: string
  status: {
    is_active: boolean
    is_archived: boolean
  }
  created_at: string
  updated_at: string
}

export interface KeywordsResponse {
  items: Keyword[]
  total: number
  page: number
  size: number
  pages: number
}

export interface RecentActivityItem {
  id: string
  type: 'comment' | 'match' | 'group' | 'keyword'
  message: string
  timestamp: string
  metadata?: any
}

export interface DashboardTopItem {
  id: number
  name: string
  count: number
  value?: number
  change?: number
}
