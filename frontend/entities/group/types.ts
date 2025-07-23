import {
  BaseEntity,
  VKGroupBase,
  VKGroupCreate,
  VKGroupUpdate,
  VKGroupResponse,
} from '@/shared/types/api'

// Re-export types from shared
export type { VKGroupBase, VKGroupCreate, VKGroupUpdate, VKGroupResponse }

export interface VKGroupStats {
  group_id: number
  total_posts: number
  total_comments: number
  comments_with_keywords: number
  last_activity?: string
  top_keywords: string[]
}
