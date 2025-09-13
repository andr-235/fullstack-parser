/**
 * API для работы с комментариями
 */

import { httpClient } from '@/shared/lib/http-client'
import type {
  Comment as VKComment,
  CommentsResponse,
  CommentFilters,
  UpdateCommentRequest,
} from '@/entities/comment'

export const commentsApi = {
  async getComments(params?: CommentFilters): Promise<CommentsResponse> {
    return httpClient.get('/api/v1/comments', params)
  },

  async getComment(id: number): Promise<VKComment> {
    return httpClient.get(`/api/v1/comments/${id}`)
  },

  async getCommentWithKeywords(commentId: number): Promise<VKComment> {
    return httpClient.get(`/api/v1/comments/${commentId}`)
  },

  async updateCommentStatus(
    commentId: number,
    statusUpdate: UpdateCommentRequest
  ): Promise<VKComment> {
    return httpClient.put(`/api/v1/comments/${commentId}`, statusUpdate)
  },

  async markCommentViewed(commentId: number): Promise<VKComment> {
    return httpClient.post(`/api/v1/comments/${commentId}/view`)
  },

  async archiveComment(commentId: number): Promise<VKComment> {
    return httpClient.post(`/api/v1/comments/${commentId}/archive`)
  },

  async unarchiveComment(commentId: number): Promise<VKComment> {
    return httpClient.post(`/api/v1/comments/${commentId}/unarchive`)
  },
}
