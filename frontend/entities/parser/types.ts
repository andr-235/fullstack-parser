export type ParserPriority = 'low' | 'normal' | 'high'

export interface ParseTaskCreate {
  group_ids: number[]
  max_posts?: number
  max_comments_per_post?: number
  force_reparse?: boolean
  priority?: ParserPriority
}

export interface ParseTaskResponse {
  task_id: string
  status: string
  group_ids: number[]
  estimated_time?: number
  created_at: string
}

export interface ParserState {
  is_running: boolean
  active_tasks: number
  queue_size: number
  total_tasks_processed: number
  total_posts_found: number
  total_comments_found: number
  last_activity?: string
  started_at?: string
  uptime_seconds: number
  overall_progress: number
}

export interface ParserStats {
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  running_tasks: number
  total_posts_found: number
  total_comments_found: number
  total_processing_time: number
  average_task_duration: number
  // Лимиты парсинга
  max_groups_per_request: number
  max_posts_per_request: number
  max_comments_per_request: number
  max_users_per_request: number
}

export type ParserGlobalStats = ParserStats

export interface ParserTasksResponse {
  items: ParseTask[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ParserHistoryResponse {
  items: ParseTask[]
  total: number
  page: number
  size: number
  pages: number
}

export type ParserSessionStatus = 'active' | 'paused' | 'completed'

export interface ParserSession {
  session_id: string
  group_id: number
  keywords: string[]
  status: ParserSessionStatus
  created_at: string
  updated_at: string
}

export interface ParseTask {
  id: string
  group_ids: number[]
  config: Record<string, unknown>
  status: string
  created_at: string
  started_at?: string
  completed_at?: string
  progress: number
  result?: Record<string, unknown>
}

export interface ParseStatus {
  task_id: string
  status: string
  progress: number
  current_group?: number
  groups_completed: number
  groups_total: number
  posts_found: number
  comments_found: number
  errors: string[]
  started_at?: string
  completed_at?: string
  duration?: number
}

export interface StopParseRequest {
  task_id?: string
}

export interface StopParseResponse {
  stopped_tasks: string[]
  message: string
}

export interface ParserTaskFilters {
  status?: string
  group_id?: number
  date_from?: string
  date_to?: string
  page?: number
  size?: number
}

export interface StartBulkParserForm {
  group_ids: number[]
  max_posts?: number
  max_comments_per_post?: number
  force_reparse?: boolean
  priority?: ParserPriority
}

export type BulkParseResponse = ParseTaskResponse

// Типы уже экспортированы выше как интерфейсы
