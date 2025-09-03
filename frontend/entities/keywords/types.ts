export interface KeywordCategory {
  name: string
  description?: string
}

export interface KeywordStatus {
  is_active: boolean
  is_archived: boolean
}

export interface Keyword {
  id: number
  word: string
  category?: KeywordCategory
  status: KeywordStatus
  description?: string
  priority: number
  match_count: number
  total_matches?: number // Для обратной совместимости
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

export type KeywordCategoryKey = (typeof KEYWORD_CATEGORIES)[number]['key']

export interface KeywordsFilters {
  active_only?: boolean
  category?: string
  search?: string
  priority_min?: number
  priority_max?: number
  match_count_min?: number
  match_count_max?: number
  page?: number
  size?: number
}

export interface KeywordsSearchRequest {
  query: string
  active_only?: boolean
  category?: string
  limit?: number
  offset?: number
}

export interface KeywordsResponse {
  items: Keyword[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CreateKeywordRequest {
  word: string
  category_name?: string
  category_description?: string
  description?: string
  priority?: number
}

export interface UpdateKeywordRequest {
  word?: string
  category_name?: string
  category_description?: string
  description?: string
  priority?: number
  is_active?: boolean
}

export interface KeywordBulkAction {
  keyword_ids: number[]
  action: 'activate' | 'deactivate' | 'archive' | 'delete'
}

export interface KeywordBulkResponse {
  total_requested: number
  successful: number
  failed: number
  errors: Array<Record<string, unknown>>
}

export interface KeywordStats {
  total_keywords: number
  active_keywords: number
  archived_keywords: number
  total_categories: number
  total_matches: number
  avg_matches_per_keyword: number
  top_categories: Array<Record<string, unknown>>
}

export interface KeywordCategoryStats {
  category_name: string
  keyword_count: number
  active_count: number
  total_matches: number
}

export interface KeywordCategoriesResponse {
  categories: string[]
  categories_with_stats: KeywordCategoryStats[]
}

export interface UploadKeywordsResponse {
  success: number
  failed: number
  errors: string[]
}
