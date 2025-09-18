/**
 * Хуки для работы с комментариями
 */

import { useReadList, useReadOne, useUpdate } from './useCrud'
import type { Comment as VKComment, CommentListResponse, CommentUpdateRequest, CommentFilters } from '@/entities/comment'

// Хук для получения списка комментариев
export function useComments(params?: CommentFilters) {
  return useReadList<CommentListResponse>('/api/v1/comments', params as Record<string, unknown>)
}

// Хук для получения одного комментария
export function useComment(id: number) {
  return useReadOne<VKComment>('/api/v1/comments', id)
}

// Хук для обновления статуса комментария
export function useUpdateCommentStatus(id: number) {
  return useUpdate<VKComment, CommentUpdateRequest>(`/api/v1/comments/${id}`, {
    successMessage: 'Статус комментария успешно обновлен',
    errorMessage: 'Ошибка при обновлении статуса комментария',
  })
}

// Хук для отметки комментария как просмотренного
export function useMarkCommentViewed(id: number) {
  return useUpdate<VKComment, void>(`/api/v1/comments/${id}/viewed`, {
    successMessage: 'Комментарий отмечен как просмотренный',
    errorMessage: 'Ошибка при отметке комментария',
  })
}

// Хук для архивирования комментария
export function useArchiveComment(id: number) {
  return useUpdate<VKComment, void>(`/api/v1/comments/${id}/archive`, {
    successMessage: 'Комментарий заархивирован',
    errorMessage: 'Ошибка при архивировании комментария',
  })
}

// Хук для разархивирования комментария
export function useUnarchiveComment(id: number) {
  return useUpdate<VKComment, void>(`/api/v1/comments/${id}/unarchive`, {
    successMessage: 'Комментарий разархивирован',
    errorMessage: 'Ошибка при разархивировании комментария',
  })
}