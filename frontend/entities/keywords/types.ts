export interface Keyword {
  word: string;
  is_active: boolean;
  category_name?: string;
  id: number;
  name: string;
  frequency: number;
  created_at: string;
  updated_at: string;
  status: {
    is_active: boolean;
  };
  category?: {
    name: string;
  };
  total_matches?: number;
  match_count?: number;
  description?: string;
}

export interface KeywordsFilters {
  search?: string;
  category?: string;
  active_only?: boolean;
  limit?: number;
}

export interface CreateKeywordRequest {
  word: string;
  category_name?: string;
  description?: string;
  priority: number;
}

export interface UpdateKeywordRequest {
  word?: string;
  category_name?: string;
  description?: string;
  priority?: number;
}

export const KEYWORD_CATEGORIES = [
  { value: 'technology', label: 'Технологии' },
  { value: 'business', label: 'Бизнес' },
  { value: 'health', label: 'Здоровье' },
  { value: 'education', label: 'Образование' },
  { value: 'entertainment', label: 'Развлечения' },
  { value: 'sports', label: 'Спорт' },
  { value: 'politics', label: 'Политика' },
  { value: 'science', label: 'Наука' },
  { value: 'other', label: 'Другое' },
] as const;

export interface UseKeywordsReturn {
  keywords: Keyword[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
  createKeyword: (request: CreateKeywordRequest) => Promise<Keyword>;
  updateKeyword: (id: number, request: UpdateKeywordRequest) => Promise<Keyword>;
  deleteKeyword: (id: number) => Promise<void>;
  toggleKeywordStatus: (id: number, isActive: boolean) => Promise<Keyword>;
}

export interface KeywordsSearchRequest {
  query: string;
  filters?: KeywordsFilters;
  limit?: number;
  offset?: number;
}

export interface KeywordStats {
  id: number;
  word: string;
  total_matches: number;
  match_count: number;
  frequency: number;
  last_updated: string;
  trend: 'up' | 'down' | 'stable';
}

export interface KeywordCategoriesResponse {
  categories: Array<{
    value: string;
    label: string;
    count?: number;
  }>;
}

export interface KeywordBulkAction {
  action: 'activate' | 'deactivate' | 'delete' | 'update_category';
  keyword_ids: number[];
  category_name?: string;
}

export interface KeywordBulkResponse {
  success: boolean;
  message: string;
  processed_count: number;
  failed_count: number;
  errors?: Array<{
    keyword_id: number;
    error: string;
  }>;
}

export interface UploadKeywordsResponse {
  success: boolean;
  message: string;
  uploaded_count: number;
  failed_count: number;
  errors?: Array<{
    row: number;
    error: string;
  }>;
}