import { ID } from '@/shared/types'

// Типы соответствующие backend схемам парсера

export interface ParseTaskCreate {
  group_id: number
  max_posts?: number
  force_reparse?: boolean
}

export interface ParseTaskResponse {
  task_id: string
  group_id: number
  group_name?: string
  status: 'running' | 'completed' | 'failed' | 'stopped'
  progress: number // от 0 до 1
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
    started_at: string
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

export interface ParserGlobalStats {
  total_groups: number
  active_groups: number
  total_keywords: number
  active_keywords: number
  total_comments: number
  comments_with_keywords: number
  last_parse_time?: string
}

// Дополнительные типы для UI
export interface ParserFilters {
  statuses?: string[]
  group_id?: number
  date_from?: string
  date_to?: string
}

export interface ParserSession {
  id: string
  task_id: string
  group_id: number
  group_name?: string
  status: ParseTaskResponse['status']
  progress: number
  started_at: string
  completed_at?: string
  stats?: ParseStats
  error_message?: string
}

export interface ParserConfig {
  max_posts_default: number
  force_reparse_default: boolean
  concurrent_tasks_limit: number
  timeout_seconds: number
}

// Типы для форм и валидации
export interface StartParserForm {
  group_id: number
  max_posts?: number
  force_reparse?: boolean
}

export interface StartBulkParserForm {
  max_posts?: number
  force_reparse?: boolean
  max_concurrent?: number
}

export interface ParserTaskFilters {
  status?: string
  group_id?: number
  date_from?: string
  date_to?: string
  page?: number
  size?: number
}

// Response types
export interface ParserTasksResponse {
  total: number
  page: number
  size: number
  items: ParseTaskResponse[]
}

export interface ParserHistoryResponse {
  total: number
  items: ParseTaskResponse[]
}

export interface BulkParseResponse {
  total_groups: number
  started_tasks: number
  failed_groups: Array<{
    group_id: number
    group_name: string
    error: string
  }>
  tasks: ParseTaskResponse[]
}
