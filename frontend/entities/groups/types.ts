import { ID } from '@/shared/types'

// Типы соответствующие backend VKGroupRead схеме
export interface VKGroup {
  id: number
  vk_id: number
  screen_name: string
  name: string
  description?: string
  is_active: boolean
  max_posts_to_check: number
  last_parsed_at?: string
  total_posts_parsed: number
  total_comments_found: number
  members_count?: number
  is_closed?: boolean
  photo_url?: string
  created_at: string
  updated_at: string
}

// Типы для создания группы
export interface CreateGroupRequest {
  vk_id_or_screen_name: string
  name?: string
  screen_name?: string
  description?: string
  is_active?: boolean
  max_posts_to_check?: number
}

// Типы для обновления группы
export interface UpdateGroupRequest {
  screen_name?: string
  name?: string
  description?: string
  is_active?: boolean
  max_posts_to_check?: number
}

// Типы для фильтров
export interface GroupsFilters {
  page?: number
  size?: number
  is_active?: boolean
  active_only?: boolean
  search?: string
}

// API Response types
export interface GroupsResponse {
  total: number
  page: number
  size: number
  items: VKGroup[]
}

// Типы для статистики группы
export interface GroupStats {
  group_id: number
  total_posts: number
  total_comments: number
  comments_with_keywords: number
  last_activity?: string
  top_keywords: string[]
}

// Типы для загрузки групп из файла
export interface UploadGroupsResponse {
  status: string
  message: string
  total_processed: number
  created: number
  skipped: number
  failed: number
  errors: string[]
  created_groups: VKGroup[]
  error_report?: any
}

// Типы для прогресса загрузки
export interface UploadProgress {
  status: string
  progress: number
  current_group: string
  total_groups: number
  processed_groups: number
  created: number
  skipped: number
  errors: string[]
}
