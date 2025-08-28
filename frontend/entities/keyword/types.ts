import { ID } from '@/shared/types'

export interface Keyword {
  id: ID
  name: string
  description?: string
  category: string
  usageCount: number
  createdAt: string
  updatedAt: string
}

export interface CreateKeywordRequest {
  name: string
  description?: string
  category: string
}

export interface UpdateKeywordRequest {
  name?: string
  description?: string
  category?: string
}
