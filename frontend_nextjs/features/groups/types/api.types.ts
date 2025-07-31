// Groups API types
import type { VKGroupResponse } from '@/types/api'
import type { GroupsUploadRequest, GroupsUploadResponse } from './groups.types'

// Базовые типы для API
export interface GroupsApiConfig {
  baseURL: string
  timeout: number
  headers: Record<string, string>
}

// Типы для запросов
export interface GetGroupsRequest {
  page?: number
  size?: number
  active_only?: boolean
  search?: string
}

export interface GetGroupRequest {
  groupId: number
}

export interface GetGroupStatsRequest {
  groupId: number
}

export interface CreateGroupRequest {
  vk_id_or_screen_name: string
  is_active: boolean
  max_posts_to_check: number
}

export interface UpdateGroupRequest {
  groupId: number
  data: {
    is_active?: boolean
    max_posts_to_check?: number
    auto_monitoring_enabled?: boolean
  }
}

export interface DeleteGroupRequest {
  groupId: number
}

export interface RefreshGroupRequest {
  groupId: number
}

// Типы для ответов
export interface GetGroupsResponse {
  items: VKGroupResponse[]
  total: number
  page: number
  size: number
}

export interface GetGroupResponse extends VKGroupResponse {}

export interface GetGroupStatsResponse {
  total_comments: number
  total_members: number
  last_parsed_at: string | null
  parsing_status: 'idle' | 'running' | 'completed' | 'failed'
}

export interface CreateGroupResponse extends VKGroupResponse {}

export interface UpdateGroupResponse extends VKGroupResponse {}

export interface DeleteGroupResponse {
  success: boolean
  message: string
}

export interface RefreshGroupResponse extends VKGroupResponse {}

// Типы для ошибок API
export interface GroupsApiError {
  status: number
  message: string
  code?: string
  details?: any
}

// Типы для пагинации
export interface GroupsPagination {
  page: number
  size: number
  total: number
  totalPages: number
}

// Типы для фильтрации
export interface GroupsApiFilters {
  search?: string
  active_only?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

// Типы для метаданных
export interface GroupsMeta {
  timestamp: string
  version: string
  cache_control?: string
}

// Типы для кэширования
export interface GroupsCacheEntry {
  data: any
  timestamp: number
  ttl: number
}

// Типы для мониторинга
export interface GroupsMonitoringConfig {
  enabled: boolean
  interval: number
  max_retries: number
  timeout: number
}

// Типы для уведомлений
export interface GroupsNotification {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  title?: string
  duration?: number
}
