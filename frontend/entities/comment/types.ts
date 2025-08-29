import { ID } from '@/shared/types'

// Типы соответствующие backend VKCommentResponse
export interface Comment {
  id: number
  vk_id: number
  text: string
  author_id: number
  author_name?: string
  author_screen_name?: string
  author_photo_url?: string
  published_at: string
  likes_count: number
  is_viewed: boolean
  is_archived: boolean
  matched_keywords_count: number
  matched_keywords?: string[]
  post_id: number
  post_vk_id?: number
  parent_comment_id?: number
  has_attachments: boolean
  is_processed: boolean
  processed_at?: string
  viewed_at?: string
  archived_at?: string
  created_at: string
  updated_at: string
  group?: {
    id: number
    name: string
    vk_id: string
    screen_name: string
  }
}

// Для обратной совместимости с существующим кодом
export interface SimpleComment {
  id: ID
  content: string
  authorId: ID
  postId: ID
  createdAt: string
  updatedAt: string
  parentId: ID | null
  likes: number
  isApproved: boolean
}

export interface CreateCommentRequest {
  content: string
  postId: ID
  parentId?: ID | null
}

export interface UpdateCommentRequest {
  is_viewed?: boolean
  is_archived?: boolean
}

export interface CommentFilters {
  page?: number
  size?: number
  text?: string
  postId?: ID
  authorId?: ID
  isApproved?: boolean
  parentId?: ID | null
  is_viewed?: boolean
  is_archived?: boolean
  group_id?: number
  keyword_id?: number
  author_screen_name?: string[]
  date_from?: string
  date_to?: string
}

// API Response types
export interface CommentsResponse {
  items: Comment[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CommentResponse extends Comment {}
