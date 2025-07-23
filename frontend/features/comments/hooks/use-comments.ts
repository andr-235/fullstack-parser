import { useQuery, useInfiniteQuery } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import type {
  VKCommentResponse,
  CommentSearchParams,
  PaginationParams,
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
    queryKey: ['comments', 'infinite', JSON.stringify(filters)],
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
    refetchOnWindowFocus: false,
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
