import {
  BaseEntity,
  VKGroupResponse,
  KeywordResponse,
} from '@/shared/types/api'

// VK Comment типы
export interface VKCommentBase {
  text: string
  author_id: number
  author_name?: string
  published_at: string
}

export interface VKCommentResponse extends VKCommentBase, BaseEntity {
  vk_id: number
  post_id: number
  post_vk_id?: number
  author_screen_name?: string
  author_photo_url?: string
  likes_count: number
  parent_comment_id?: number
  has_attachments: boolean
  matched_keywords_count: number
  is_processed: boolean
  processed_at?: string
  group?: VKGroupResponse
  matched_keywords?: KeywordResponse[]
}

export interface CommentWithKeywords extends VKCommentResponse {
  matched_keywords: KeywordResponse[]
  keyword_matches: Array<{
    keyword: string
    matched_text: string
    position: number
    context: string
  }>
}

export interface CommentSearchParams {
  text?: string
  group_id?: number
  keyword_id?: number
  author_id?: number
  date_from?: string
  date_to?: string
}
