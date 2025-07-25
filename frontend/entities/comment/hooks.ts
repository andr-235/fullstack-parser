import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type {
  VKCommentResponse,
  CommentSearchParams,
  PaginationParams,
  PaginatedResponse,
} from '@/types/api'

// Хук для получения комментариев
export function useComments(params?: CommentSearchParams & PaginationParams) {
  const { page = 1, size = 20, ...filters } = params || {}

  return useQuery({
    queryKey: ['comments', { page, size, ...filters }],
    queryFn: () => {
      const searchParams = new URLSearchParams()
      searchParams.append('page', page.toString())
      searchParams.append('size', size.toString())

      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach((v) => searchParams.append(key, v))
          } else {
            searchParams.append(key, value.toString())
          }
        }
      })

      return api.get<PaginatedResponse<VKCommentResponse>>(
        `/comments?${searchParams.toString()}`
      )
    },
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

// Хук для бесконечной прокрутки комментариев
export function useInfiniteComments(filters?: CommentSearchParams) {
  return useInfiniteQuery({
    queryKey: ['infinite-comments', filters],
    queryFn: ({ pageParam = 1 }) => {
      const searchParams = new URLSearchParams()
      searchParams.append('page', pageParam.toString())
      searchParams.append('size', '20')

      Object.entries(filters || {}).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach((v) => searchParams.append(key, v))
          } else {
            searchParams.append(key, value.toString())
          }
        }
      })

      return api.get<PaginatedResponse<VKCommentResponse>>(
        `/comments?${searchParams.toString()}`
      )
    },
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce(
        (acc, page) => acc + page.data.items.length,
        0
      )
      if (loaded < (lastPage?.data.total || 0)) {
        return allPages.length + 1
      }
      return undefined
    },
    initialPageParam: 1,
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

// Хук для обновления статуса комментария
export function useUpdateCommentStatus() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      commentId,
      data,
    }: {
      commentId: number
      data: { is_viewed?: boolean; is_archived?: boolean }
    }) => api.patch<VKCommentResponse>(`/comments/${commentId}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
      queryClient.invalidateQueries({ queryKey: ['infinite-comments'] })
    },
  })
}

// Хук для отметки комментария как просмотренного
export function useMarkCommentAsViewed() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentId: number) =>
      api.patch<VKCommentResponse>(`/comments/${commentId}`, {
        is_viewed: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
      queryClient.invalidateQueries({ queryKey: ['infinite-comments'] })
    },
  })
}

// Хук для архивирования комментария
export function useArchiveComment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentId: number) =>
      api.patch<VKCommentResponse>(`/comments/${commentId}`, {
        is_archived: true,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
      queryClient.invalidateQueries({ queryKey: ['infinite-comments'] })
    },
  })
}

// Хук для разархивирования комментария
export function useUnarchiveComment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentId: number) =>
      api.patch<VKCommentResponse>(`/comments/${commentId}`, {
        is_archived: false,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
      queryClient.invalidateQueries({ queryKey: ['infinite-comments'] })
    },
  })
}

// Хук для получения комментария с ключевыми словами
export function useCommentWithKeywords(commentId: number) {
  return useQuery({
    queryKey: ['comment-with-keywords', commentId],
    queryFn: () => api.get<any>(`/comments/${commentId}/keywords`),
    enabled: !!commentId,
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}
