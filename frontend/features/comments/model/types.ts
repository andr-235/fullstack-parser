/**
 * Типы для модуля Comments
 */

// Базовые типы комментариев
export interface Comment {
  id: number;
  vk_id: number;
  post_id: number;
  author_id: number;
  text: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  author?: Author;
}

export interface Author {
  id: number;
  vk_id: number;
  first_name: string;
  last_name: string;
  photo_url?: string;
}

// Запросы
export interface CommentCreate {
  vk_id: number;
  post_id: number;
  author_id: number;
  text: string;
}

export interface CommentUpdate {
  text?: string;
  is_deleted?: boolean;
}

export interface CommentFilter {
  group_id?: number;
  post_id?: number;
  author_id?: number;
  search_text?: string;
  is_deleted?: boolean;
}

// Ответы API
export interface CommentResponse {
  id: number;
  vk_id: number;
  post_id: number;
  author_id: number;
  text: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  author?: Author;
}

export interface CommentListResponse {
  items: CommentResponse[];
  total: number;
  page: number;
  limit: number;
}

export interface CommentStats {
  total_comments: number;
  comments_today: number;
  comments_this_week: number;
  comments_this_month: number;
  average_comments_per_post: number;
  top_authors: Array<{
    author_id: number;
    author_name: string;
    comments_count: number;
  }>;
}

// Анализ ключевых слов
export interface KeywordAnalysisRequest {
  comment_id: number;
  keywords: string[];
}

export interface KeywordAnalysisResponse {
  comment_id: number;
  found_keywords: string[];
  keyword_matches: Array<{
    keyword: string;
    count: number;
    positions: number[];
  }>;
  analysis_score: number;
}

export interface BatchKeywordAnalysisRequest {
  comment_ids: number[];
  keywords: string[];
}

export interface BatchKeywordAnalysisResponse {
  analyses: KeywordAnalysisResponse[];
  total_analyzed: number;
  success_count: number;
  error_count: number;
}

export interface KeywordSearchRequest {
  keywords: string[];
  group_id?: number;
  post_id?: number;
  limit?: number;
  offset?: number;
}

export interface KeywordSearchResponse {
  comments: CommentResponse[];
  total: number;
  keyword_matches: Array<{
    comment_id: number;
    matched_keywords: string[];
  }>;
}

export interface KeywordStatisticsResponse {
  total_keywords_analyzed: number;
  most_frequent_keywords: Array<{
    keyword: string;
    frequency: number;
    percentage: number;
  }>;
  analysis_coverage: number;
}

// Метрики
export interface CommentsMetrics {
  total_comments: number;
  growth_percentage: number;
  trend: string;
}

// Параметры запросов
export interface GetCommentsParams {
  group_id?: number;
  post_id?: number;
  author_id?: number;
  search_text?: string;
  is_deleted?: boolean;
  include_author?: boolean;
  limit?: number;
  offset?: number;
}

export interface GetCommentParams {
  include_author?: boolean;
}
