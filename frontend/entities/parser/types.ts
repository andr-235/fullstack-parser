export interface ParseTaskCreate {
  group_id: number
  keywords?: string[]
  max_posts?: number
  start_date?: string
  end_date?: string
  forceReparse?: boolean
}

export interface ParseTaskResponse {
  task_id: string
  status: 'pending' | 'running' | 'stopped' | 'completed' | 'failed'
  progress: number
  message?: string
  group_id?: number
  group_name?: string
  posts_processed?: number
  started_at: string
  error_message?: string
  stats?: {
    posts_processed: number
    comments_found: number
  }
  created_at: string
  updated_at: string
  result?: any
}

export interface ParserState {
  is_running: boolean
  status?: 'running' | 'stopped' | 'failed'
  current_task?: ParseTaskResponse
  task?: ParseTaskResponse
  queue_length: number
  last_activity: string
  task_id?: string
  started_at?: string
  posts_processed?: number
  group_name?: string
  group_id?: number
  progress?: number
}

export interface ParserStats {
  total_parsed: number
  total_posts_processed: number
  comments_found: number
  matches_found: number
  errors_count: number
  total_runs: number
  successful_runs: number
  avg_processing_time: number
  average_duration: number
}

export interface ParserGlobalStats {
  active_tasks: number
  total_tasks: number
  total_comments: number
  total_posts_processed: number
  comments_with_keywords: number
  completed_today: number
  failed_today: number
  active_groups: number
  total_groups: number
  active_keywords: number
  total_keywords: number
  last_parse_time?: string
  avg_completion_time: number
}

export interface ParserTasksResponse {
  items: ParseTaskResponse[]
  total: number
  page: number
  size: number
}

export interface ParserHistoryResponse {
  items: ParseTaskResponse[]
  total: number
  page: number
  size: number
}

export interface ParserSession {
  session_id: string
  group_id: number
  keywords: string[]
  status: 'active' | 'paused' | 'completed'
  created_at: string
  updated_at: string
}

export interface ParserTaskFilters {
  status?: 'pending' | 'running' | 'completed' | 'failed'
  group_id?: number
  date_from?: string
  date_to?: string
  page?: number
  size?: number
}

export interface StartBulkParserForm {
  groups: number[]
  keywords: string[]
  max_posts_per_group?: number
  max_posts?: number
  start_date?: string
  end_date?: string
  forceReparse?: boolean
}

export interface BulkParseResponse {
  task_ids: string[]
  total_groups: number
  total_keywords: number
  estimated_time: number
  started_tasks: number
  failed_groups: string[]
}
