import { BaseEntity } from '@/shared/types/api'

// VK Group типы
export interface VKGroupBase {
  screen_name: string
  name: string
  description?: string
  is_active: boolean
  max_posts_to_check: number
}

export interface VKGroupCreate extends VKGroupBase {
  vk_id_or_screen_name: string
}

export interface VKGroupUpdate {
  name?: string
  description?: string
  is_active?: boolean
  max_posts_to_check?: number
}

export interface VKGroupResponse extends VKGroupBase, BaseEntity {
  vk_id: number
  last_parsed_at?: string
  total_posts_parsed: number
  total_comments_found: number
  members_count?: number
  is_closed: boolean
  photo_url?: string
}

export interface VKGroupStats {
  group_id: number
  total_posts: number
  total_comments: number
  comments_with_keywords: number
  last_activity?: string
  top_keywords: string[]
} 