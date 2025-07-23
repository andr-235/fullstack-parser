// Groups feature types
import type { VKGroupResponse } from '@/types/api'

// Props для компонентов
export interface GroupsHeaderProps {
  title?: string
  description?: string
}

export interface GroupsStatsData {
  totalGroups: number
  activeGroups: number
  inactiveGroups: number
}

export interface GroupsManagementProps {
  searchTerm: string
  onSearchChange: (value: string) => void
  activeOnly: boolean
  onActiveOnlyChange: (value: boolean) => void
}

export interface CollapsibleSectionProps {
  title: string
  icon: React.ElementType
  children: React.ReactNode
  defaultExpanded?: boolean
}

// Типы для сортировки
export type SortField = 'comments' | 'members' | 'name' | 'last_parsed'
export type SortOrder = 'asc' | 'desc'

export interface SortConfig {
  field: SortField
  order: SortOrder
}

// Типы для фильтров
export interface GroupsFilters {
  search?: string
  activeOnly?: boolean
  pageSize?: number
}

// Типы для действий с группами
export interface GroupAction {
  id: number
  type: 'toggle' | 'delete' | 'refresh'
  data?: any
}

// Типы для статистики
export interface GroupsStats {
  total: number
  active: number
  inactive: number
  totalComments: number
  totalMembers: number
}

// Типы для состояния UI
export interface GroupsUIState {
  searchTerm: string
  activeOnly: boolean
  sortBy: SortField
  sortOrder: SortOrder
  copiedGroup: string | null
  selectedGroups: number[]
}

// Типы для API ответов (расширяем базовые)
export interface GroupsListResponse {
  items: VKGroupResponse[]
  total: number
  page: number
  size: number
}

export interface GroupCreateRequest {
  vk_id_or_screen_name: string
  is_active: boolean
  max_posts_to_check: number
}

export interface GroupUpdateRequest {
  is_active?: boolean
  max_posts_to_check?: number
  auto_monitoring_enabled?: boolean
}

// Типы для ошибок
export interface GroupsError {
  code: string
  message: string
  details?: any
}

// Типы для загрузки файлов
export interface GroupsUploadRequest {
  file: File
  options: {
    is_active: boolean
    max_posts_to_check: number
  }
}

export interface GroupsUploadResponse {
  message: string
  total_processed: number
  created: number
  skipped: number
  errors: string[]
}
