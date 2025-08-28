import { ID } from '@/shared/types'

export interface Comment {
  id: ID
  content: string
  authorId: ID
  postId: ID
  createdAt: string
  updatedAt: string
  parentId?: ID
  likes: number
  isApproved: boolean
}

export interface CreateCommentRequest {
  content: string
  postId: ID
  parentId?: ID
}

export interface UpdateCommentRequest {
  content: string
  isApproved?: boolean
}

export interface CommentFilters {
  postId?: ID
  authorId?: ID
  isApproved?: boolean
  parentId?: ID
}
