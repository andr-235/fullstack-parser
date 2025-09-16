export interface Author {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  vk_id?: string;
  posts_count?: number;
  followers_count?: number;
  created_at: string;
  updated_at: string;
  is_verified?: boolean;
}

export interface AuthorCreateRequest {
  name: string;
  description?: string;
  avatar_url?: string;
  vk_id?: string;
}

export interface AuthorUpdateRequest {
  name?: string;
  description?: string;
  avatar_url?: string;
  is_verified?: boolean;
}

export interface AuthorListResponse {
  authors: Author[];
  total: number;
  page: number;
  limit: number;
}

export interface AuthorFilters {
  name?: string;
  vk_id?: string;
  is_verified?: boolean;
  limit?: number;
  offset?: number;
  sort_by?: 'name' | 'posts_count' | 'followers_count' | 'created_at';
  sort_order?: 'asc' | 'desc';
}