export interface VKCommentResponse {
  id: number;
  vk_id: number;
  group_id: number;
  group_name: string;
  post_id: number;
  author_id: number;
  author_name: string;
  author_photo: string;
  text: string;
  date: string;
  likes_count: number;
  is_viewed: boolean;
  is_archived: boolean;
  keywords_found: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
  created_at: string;
  updated_at: string;
}

export interface CommentSearchParams {
  group_id?: number;
  post_id?: number;
  author_id?: number;
  keywords?: string[];
  date_from?: string;
  date_to?: string;
  is_viewed?: boolean;
  is_archived?: boolean;
  sentiment?: 'positive' | 'negative' | 'neutral';
  search?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CommentWithKeywords extends VKCommentResponse {
  matched_keywords: {
    keyword: string;
    category: string;
    priority: 'low' | 'medium' | 'high';
  }[];
}

export interface CommentStats {
  total_comments: number;
  viewed_comments: number;
  archived_comments: number;
  comments_with_keywords: number;
  positive_sentiment_count: number;
  negative_sentiment_count: number;
  neutral_sentiment_count: number;
  top_groups: { group_id: number; group_name: string; comment_count: number }[];
  top_keywords: { keyword: string; count: number }[];
}
