/**
 * Базовые типы API на основе FastAPI схем backend
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

export interface APIError {
  detail: string
  status_code: number
}

export interface PaginationParams {
  page?: number
  size?: number
}

// VK Group типы
export interface VKGroupBase {
  screen_name: string
  name: string
  description?: string
  is_active: boolean
  max_posts_to_check: number
}

export interface VKGroupCreate extends VKGroupBase {
  vk_id_or_screen_name: string
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
