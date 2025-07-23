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
    onMutate: async ({ commentId, statusUpdate }) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey: ['comments'] })

      // Сохраняем предыдущее состояние
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      // Оптимистично обновляем кеш
      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              comment.id === commentId
                ? {
                    ...comment,
                    ...statusUpdate,
                    viewed_at: statusUpdate.is_viewed
                      ? new Date().toISOString()
                      : comment.viewed_at,
                    archived_at: statusUpdate.is_archived
                      ? new Date().toISOString()
                      : comment.archived_at,
                  }
                : comment
            ),
          })),
        }
      })

      return { previousComments }
    },
    onError: (err, variables, context) => {
      // Восстанавливаем предыдущее состояние при ошибке
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      // Инвалидируем кеш для синхронизации с сервером
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
    onMutate: async (commentId) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey: ['comments'] })

      // Сохраняем предыдущее состояние
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      // Оптимистично обновляем кеш
      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              comment.id === commentId
                ? {
                    ...comment,
                    is_viewed: true,
                    viewed_at: new Date().toISOString(),
                  }
                : comment
            ),
          })),
        }
      })

      return { previousComments }
    },
    onError: (err, variables, context) => {
      console.error('Ошибка при отметке комментария как просмотренного:', err)
      // Восстанавливаем предыдущее состояние при ошибке
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      // Инвалидируем кеш для синхронизации с сервером
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
    onMutate: async (commentId) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey: ['comments'] })

      // Сохраняем предыдущее состояние
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      // Оптимистично обновляем кеш
      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              comment.id === commentId
                ? {
                    ...comment,
                    is_viewed: true,
                    is_archived: true,
                    viewed_at: new Date().toISOString(),
                    archived_at: new Date().toISOString(),
                  }
                : comment
            ),
          })),
        }
      })

      return { previousComments }
    },
    onError: (err, variables, context) => {
      console.error('Ошибка при архивировании комментария:', err)
      // Восстанавливаем предыдущее состояние при ошибке
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      // Инвалидируем кеш для синхронизации с сервером
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
    onMutate: async (commentId) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey: ['comments'] })

      // Сохраняем предыдущее состояние
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      // Оптимистично обновляем кеш
      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              comment.id === commentId
                ? {
                    ...comment,
                    is_archived: false,
                    archived_at: null,
                  }
                : comment
            ),
          })),
        }
      })

      return { previousComments }
    },
    onError: (err, variables, context) => {
      console.error('Ошибка при разархивировании комментария:', err)
      // Восстанавливаем предыдущее состояние при ошибке
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      // Инвалидируем кеш для синхронизации с сервером
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
