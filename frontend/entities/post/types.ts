export interface Post {
  id: string;
  title: string;
  content: string;
  author_id: string;
  group_id?: string;
  created_at: string;
  updated_at: string;
  likes_count?: number;
  comments_count?: number;
  shares_count?: number;
  is_pinned?: boolean;
  tags?: string[];
}

export interface PostCreateRequest {
  title: string;
  content: string;
  group_id?: string;
  tags?: string[];
}

export interface PostUpdateRequest {
  title?: string;
  content?: string;
  tags?: string[];
  is_pinned?: boolean;
}

export interface PostListResponse {
  posts: Post[];
  total: number;
  page: number;
  limit: number;
}

export interface PostFilters {
  author_id?: string;
  group_id?: string;
  tags?: string[];
  limit?: number;
  offset?: number;
  sort_by?: 'created_at' | 'likes_count' | 'comments_count';
  sort_order?: 'asc' | 'desc';
}