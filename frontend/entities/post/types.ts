import { ID } from '@/shared/types'

export type PostStatus = 'draft' | 'published' | 'archived'

export interface Post {
  id: ID
  title: string
  content: string
  authorId: ID
  groupId?: ID
  keywordIds: ID[]
  status: PostStatus
  createdAt: string
  updatedAt: string
  publishedAt?: string
}

export interface CreatePostRequest {
  title: string
  content: string
  groupId?: ID
  keywordIds?: ID[]
  status?: PostStatus
}

export interface UpdatePostRequest {
  title?: string
  content?: string
  groupId?: ID
  keywordIds?: ID[]
  status?: PostStatus
}
