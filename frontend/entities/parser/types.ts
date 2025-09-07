export interface ParseTaskCreate {
  group_ids: number[]
  max_posts?: number
  max_comments_per_post?: number
  force_reparse?: boolean
  priority?: 'low' | 'normal' | 'high'
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
  uptime_seconds: number
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

export interface ParserGlobalStats extends ParserStats {
  // Наследует все поля из ParserStats
}

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

export interface ParserSession {
  session_id: string
  group_id: number
  keywords: string[]
  status: 'active' | 'paused' | 'completed'
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
  priority?: 'low' | 'normal' | 'high'
}

export interface BulkParseResponse extends ParseTaskResponse {
  // Наследует все поля из ParseTaskResponse
}

// Типы уже экспортированы выше как интерфейсы
