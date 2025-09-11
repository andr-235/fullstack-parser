export interface Comment {
  id: number
  text: string
  author: string
  author_name?: string
  author_screen_name?: string
  author_photo_url?: string
  post_id: number
  vk_id?: string
  post_vk_id?: string
  group_id: number
  group?: any
  date: string
  published_at?: string
  is_viewed: boolean
  is_archived?: boolean
  sentiment?: string
  keywords?: string[]
  matched_keywords?: string[]
  matched_keywords_count: number
  likes_count?: number
  parent_comment_id?: number
}

export interface CreateCommentRequest {
  text: string
  post_id: number
  group_id: number
  author?: string
}

export interface UpdateCommentRequest {
  is_viewed?: boolean
  sentiment?: string
}

export interface CommentFilters {
  is_viewed?: boolean
  group_id?: number
  post_id?: number
  keyword_id?: number
  limit?: number
  offset?: number
  page?: number
  size?: number
  text?: string
  authorId?: number
  date_from?: string
  date_to?: string
  is_archived?: boolean
  has_keywords?: boolean // Фильтр для показа только комментариев с ключевыми словами
}

export interface CommentsResponse {
  items: Comment[]
  total: number
  limit: number
  offset: number
}
