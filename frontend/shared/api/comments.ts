/**
 * API для работы с комментариями
 */

import { httpClient } from '@/shared/lib/http-client'
import { getRoutePath, COMMENTS_ROUTES } from '@/shared/config/routes'
import type {
  Comment as VKComment,
  CommentsResponse,
  CommentFilters,
  UpdateCommentRequest,
} from '@/entities/comment'

export const commentsApi = {
  async getComments(params?: CommentFilters): Promise<CommentsResponse> {
    return httpClient.get(getRoutePath(COMMENTS_ROUTES.LIST), params)
  },

  async getComment(id: number): Promise<VKComment> {
    return httpClient.get(getRoutePath(COMMENTS_ROUTES.GET(id)))
  },

  async getCommentWithKeywords(commentId: number): Promise<VKComment> {
    return httpClient.get(getRoutePath(COMMENTS_ROUTES.GET(commentId)))
  },

  async updateCommentStatus(
    commentId: number,
    statusUpdate: UpdateCommentRequest
  ): Promise<VKComment> {
    return httpClient.put(getRoutePath(COMMENTS_ROUTES.UPDATE(commentId)), statusUpdate)
  },

  async markCommentViewed(commentId: number): Promise<VKComment> {
    return httpClient.post(getRoutePath(COMMENTS_ROUTES.VIEW(commentId)))
  },

  async archiveComment(commentId: number): Promise<VKComment> {
    return httpClient.post(getRoutePath(COMMENTS_ROUTES.ARCHIVE(commentId)))
  },

  async unarchiveComment(commentId: number): Promise<VKComment> {
    return httpClient.post(getRoutePath(COMMENTS_ROUTES.UNARCHIVE(commentId)))
  },
}
