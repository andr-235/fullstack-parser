import {
  useQuery,
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import type {
  VKCommentResponse,
  CommentSearchParams,
  PaginationParams,
  CommentUpdateRequest,
} from '@/types/api'

/**
 * Хук для получения комментариев с пагинацией
 */
export function useComments(params?: CommentSearchParams & PaginationParams) {
  return useQuery({
    queryKey: createQueryKey.comments(params),
    queryFn: () => api.getComments(params),
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

/**
 * Хук для бесконечной загрузки комментариев
 */
export function useInfiniteComments(filters?: CommentSearchParams) {
  return useInfiniteQuery({
    queryKey: ['comments', 'infinite', filters],
    queryFn: ({ pageParam = 1 }) =>
      api.getComments({
        ...filters,
        page: pageParam,
        size: 20,
      }),
    getNextPageParam: (lastPage, pages) => {
      const totalLoaded = pages.length * 20
      return lastPage.total > totalLoaded ? pages.length + 1 : undefined
    },
    initialPageParam: 1,
    staleTime: 2 * 60 * 1000,
  })
}

/**
 * Хук для обновления статуса комментария
 */
export function useUpdateCommentStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      commentId,
      statusUpdate,
    }: {
      commentId: number
      statusUpdate: CommentUpdateRequest
    }) => api.updateCommentStatus(commentId, statusUpdate),
    onSuccess: () => {
      // Инвалидируем кеш комментариев
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для отметки комментария как просмотренного
 */
export function useMarkCommentAsViewed() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentId: number) => api.markCommentAsViewed(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для архивирования комментария
 */
export function useArchiveComment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentId: number) => api.archiveComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для разархивирования комментария
 */
export function useUnarchiveComment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentId: number) => api.unarchiveComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для получения конкретного комментария с ключевыми словами
 */
export function useCommentWithKeywords(commentId: number) {
  return useQuery({
    queryKey: createQueryKey.comment(commentId),
    queryFn: () => api.getCommentWithKeywords(commentId),
    enabled: !!commentId,
    staleTime: 5 * 60 * 1000,
  })
}
