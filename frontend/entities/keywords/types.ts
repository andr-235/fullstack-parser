import { ID } from '@/shared/types'

// Типы соответствующие backend KeywordResponse схеме
export interface Keyword {
  id: number
  word: string
  category?: string
  description?: string
  is_active: boolean
  is_case_sensitive: boolean
  is_whole_word: boolean
  total_matches: number
  created_at: string
  updated_at: string
}

// Типы для создания keyword
export interface CreateKeywordRequest {
  word: string
  category?: string
  description?: string
  is_active?: boolean
  is_case_sensitive?: boolean
  is_whole_word?: boolean
}

// Типы для обновления keyword
export interface UpdateKeywordRequest {
  word?: string
  category?: string
  description?: string
  is_active?: boolean
  is_case_sensitive?: boolean
  is_whole_word?: boolean
}

// Типы для фильтров
export interface KeywordsFilters {
  page?: number
  size?: number
  active_only?: boolean
  category?: string
  search?: string
}

// API Response types
export interface KeywordsResponse {
  total: number
  page: number
  size: number
  items: Keyword[]
}

// Типы для загрузки keywords из файла
export interface UploadKeywordsResponse {
  status: string
  message: string
  total_processed: number
  created: number
  skipped: number
  errors: string[]
  created_keywords: Keyword[]
}

// Типы для статистики keyword
export interface KeywordStats {
  keyword_id: number
  word: string
  total_matches: number
  recent_matches: number
  top_groups: string[]
}

// Категории ключевых слов
export const KEYWORD_CATEGORIES = [
  'Общие',
  'Технические',
  'Маркетинговые',
  'Продажи',
  'Поддержка',
  'Баги',
  'Рекомендации',
  'Жалобы',
  'Благодарности',
] as const

export type KeywordCategory = (typeof KEYWORD_CATEGORIES)[number]
