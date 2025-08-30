export interface Keyword {
  id: number
  keyword: string
  word?: string
  category?: string
  is_active: boolean
  is_case_sensitive?: boolean
  is_whole_word?: boolean
  total_matches: number
  description?: string
  created_at: string
  updated_at: string
}

export const KEYWORD_CATEGORIES = [
  { key: 'general', label: 'Общие' },
  { key: 'business', label: 'Бизнес' },
  { key: 'technology', label: 'Технологии' },
  { key: 'politics', label: 'Политика' },
  { key: 'sports', label: 'Спорт' },
  { key: 'entertainment', label: 'Развлечения' },
  { key: 'health', label: 'Здоровье' },
  { key: 'education', label: 'Образование' },
] as const

// Для обратной совместимости
export const KEYWORD_CATEGORIES_MAP = {
  general: 'Общие',
  business: 'Бизнес',
  technology: 'Технологии',
  politics: 'Политика',
  sports: 'Спорт',
  entertainment: 'Развлечения',
  health: 'Здоровье',
  education: 'Образование',
} as const

export type KeywordCategory = (typeof KEYWORD_CATEGORIES)[number]['key']

export interface KeywordsFilters {
  is_active?: boolean
  active_only?: boolean
  category?: string
  search?: string
  page?: number
  size?: number
}

export interface KeywordsResponse {
  items: Keyword[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface CreateKeywordRequest {
  keyword: string
  category?: string
  is_active?: boolean
}

export interface UpdateKeywordRequest {
  keyword?: string
  word?: string
  category?: string
  is_active?: boolean
  is_case_sensitive?: boolean
  is_whole_word?: boolean
  description?: string
}

export interface KeywordStats {
  total_keywords: number
  active_keywords: number
  inactive_keywords: number
}

export interface UploadKeywordsResponse {
  success: number
  failed: number
  errors: string[]
}
