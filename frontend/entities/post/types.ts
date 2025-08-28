import { ID } from '@/shared/types'

export interface Post {
  id: ID
  title: string
  content: string
  authorId: ID
  groupId?: ID
  keywordIds: ID[]
  status: 'draft' | 'published' | 'archived'
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

export interface CreatePostRequest {
  title: string
  content: string
  groupId?: ID
  keywordIds?: ID[]
  status?: Post['status']
}

export interface UpdatePostRequest {
  title?: string
  content?: string
  groupId?: ID
  keywordIds?: ID[]
  status?: Post['status']
}
