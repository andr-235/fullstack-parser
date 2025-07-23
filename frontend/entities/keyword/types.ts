import { BaseEntity, KeywordBase, KeywordCreate, KeywordUpdate, KeywordResponse } from '@/shared/types/api'

// Re-export types from shared
export type {
  KeywordBase,
  KeywordCreate,
  KeywordUpdate,
  KeywordResponse
}

export interface KeywordStats {
  keyword_id: number
  word: string
  total_matches: number
  recent_matches: number
  top_groups: string[]
}
