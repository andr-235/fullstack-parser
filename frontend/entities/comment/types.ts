export interface Comment {
  id: string;
  text: string;
  author_id: string;
  post_id: string;
  created_at: string;
  updated_at: string;
  likes_count?: number;
  replies_count?: number;
  parent_id?: string;
}

export interface CommentCreateRequest {
  text: string;
  post_id: string;
  parent_id?: string;
}

export interface CommentUpdateRequest {
  text: string;
}

export interface CommentListResponse {
  comments: Comment[];
  total: number;
  page: number;
  limit: number;
}

export interface CommentFilters {
  post_id?: string;
  author_id?: string;
  parent_id?: string;
  limit?: number;
  offset?: number;
}