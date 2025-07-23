/**
 * Типы API на основе FastAPI схем backend
 */

// Базовые типы
export interface BaseEntity {
  id: number
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  size: number
  items: T[]
}

export interface StatusResponse {
  success: boolean
  message: string
}

// VK Group типы
export interface VKGroupBase {
  screen_name: string
  name: string
  description?: string
  is_active: boolean
  max_posts_to_check: number
}

export interface VKGroupCreate {
  vk_id_or_screen_name: string
  name?: string
  screen_name?: string
  description?: string
  is_active: boolean
  max_posts_to_check: number
}

export interface VKGroupUpdate {
  name?: string
  description?: string
  is_active?: boolean
  max_posts_to_check?: number
}

export interface VKGroupResponse extends VKGroupBase, BaseEntity {
  vk_id: number
  last_parsed_at?: string
  total_posts_parsed: number
  total_comments_found: number
  members_count?: number
  is_closed: boolean
  photo_url?: string
}

export interface VKGroupStats {
  group_id: number
  total_posts: number
  total_comments: number
  comments_with_keywords: number
  last_activity?: string
  top_keywords: string[]
}

export interface VKGroupUploadResponse {
  status: string
  message: string
  total_processed: number
  created: number
  skipped: number
  errors: string[]
  created_groups: VKGroupResponse[]
}

// Keyword типы
export interface KeywordBase {
  word: string
  category?: string
  description?: string
  is_active: boolean
  is_case_sensitive: boolean
  is_whole_word: boolean
}

export interface KeywordCreate extends KeywordBase {}

export interface KeywordUpdate {
  word?: string
  category?: string
  description?: string
  is_active?: boolean
  is_case_sensitive?: boolean
  is_whole_word?: boolean
}

export interface KeywordResponse extends KeywordBase, BaseEntity {
  total_matches: number
}

export interface KeywordUploadResponse {
  status: string
  message: string
  total_processed: number
  created: number
  skipped: number
  errors: string[]
  created_keywords: KeywordResponse[]
}

export interface KeywordStats {
  keyword_id: number
  word: string
  total_matches: number
  recent_matches: number
  top_groups: string[]
  author_screen_name?: string
  author_photo_url?: string
  likes_count: number
  parent_comment_id?: number
  has_attachments: boolean
  matched_keywords_count: number
  is_processed: boolean
  processed_at?: string
  group?: VKGroupResponse
  matched_keywords?: KeywordResponse[]
}

// VK Comment типы
export interface VKCommentBase {
  text: string
  author_id: number
  author_name?: string
  published_at: string
}

export interface VKCommentResponse extends VKCommentBase, BaseEntity {
  vk_id: number
  post_id: number
  post_vk_id?: number
  author_screen_name?: string
  author_photo_url?: string
  likes_count: number
  parent_comment_id?: number
  has_attachments: boolean
  matched_keywords_count: number
  is_processed: boolean
  processed_at?: string
  is_viewed: boolean
  viewed_at?: string
  is_archived: boolean
  archived_at?: string
  group?: VKGroupResponse
  matched_keywords?: string[]
}

export interface CommentWithKeywords extends VKCommentResponse {
  matched_keywords: string[]
  keyword_matches: Array<{
    keyword: string
    matched_text: string
    position: number
    context: string
  }>
}

export interface CommentUpdateRequest {
  is_viewed?: boolean
  is_archived?: boolean
}

export interface CommentSearchParams {
  text?: string
  group_id?: number
  keyword_id?: number
  author_id?: number
  author_screen_name?: string[]
  date_from?: string
  date_to?: string
  is_viewed?: boolean
  is_archived?: boolean
}

// Parser типы
export interface ParseTaskCreate {
  group_id: number
  max_posts?: number
  force_reparse?: boolean
}

export interface ParseTaskResponse {
  task_id: string
  group_id: number
  group_name?: string
  status: 'running' | 'completed' | 'failed'
  started_at: string
  completed_at?: string
  stats?: ParseStats
  error_message?: string
}

export interface ParseStats {
  posts_processed: number
  comments_found: number
  comments_with_keywords: number
  new_comments: number
  keyword_matches: number
  duration_seconds?: number
}

export interface ParserState {
  status: 'running' | 'stopped' | 'failed'
  task?: {
    task_id: string
    group_id: number
    group_name?: string
    progress: number
    posts_processed: number
  }
}

export interface ParserStats {
  total_runs: number
  successful_runs: number
  failed_runs: number
  average_duration: number
  total_posts_processed: number
  total_comments_found: number
  total_comments_with_keywords: number
}

export interface GlobalStats {
  total_groups: number
  active_groups: number
  total_keywords: number
  active_keywords: number
  total_comments: number
  comments_with_keywords: number
  last_parse_time?: string
}

export interface DashboardStats {
  today_comments: number
  today_matches: number
  week_comments: number
  week_matches: number
  top_groups: Array<{ name: string; count: number }>
  top_keywords: Array<{ word: string; count: number }>
  recent_activity: Array<{
    id: number
    type: 'parse' | 'comment' | 'group'
    message: string
    timestamp: string
  }>
}

// API Error типы
export interface APIError {
  detail: string
  status_code: number
}

// Пагинация
export interface PaginationParams {
  page?: number
  size?: number
}

// Monitoring типы
export interface MonitoringStats {
  total_groups: number
  active_groups: number
  monitored_groups: number
  ready_for_monitoring: number
  next_monitoring_at?: string
  next_monitoring_at_local?: string // Локальное время Владивостока
}

export interface VKGroupMonitoring extends VKGroupResponse {
  id: number // Добавляем id для совместимости с frontend
  group_id?: number // Оставляем group_id для совместимости с API
  auto_monitoring_enabled: boolean
  monitoring_interval_minutes: number
  monitoring_priority: number
  next_monitoring_at?: string
  next_monitoring_at_local?: string // Локальное время Владивостока
  monitoring_runs_count: number
  last_monitoring_success?: string
  last_monitoring_success_local?: string // Локальное время Владивостока
  last_monitoring_error?: string
}

export interface MonitoringGroupUpdate {
  auto_monitoring_enabled?: boolean
  monitoring_interval_minutes?: number
  monitoring_priority?: number
}

export interface MonitoringRunResult {
  total_groups: number
  monitored_groups: number
  successful_runs: number
  failed_runs: number
  duration_seconds: number
}

export interface SchedulerStatus {
  is_running: boolean
  monitoring_interval_seconds: number
  redis_connected: boolean
  last_check: string
}
