import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type { VKCommentResponse } from '@/types/api'

/**
 * Хук для массовой отметки комментариев как просмотренных
 */
export function useBulkMarkAsViewed() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentIds: number[]) =>
      api.bulkMarkCommentsAsViewed(commentIds),
    onMutate: async (commentIds) => {
      await queryClient.cancelQueries({ queryKey: ['comments'] })
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              commentIds.includes(comment.id)
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
      console.error(
        'Ошибка при массовой отметке комментариев как просмотренных:',
        err
      )
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для массового архивирования комментариев
 */
export function useBulkArchive() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentIds: number[]) => api.bulkArchiveComments(commentIds),
    onMutate: async (commentIds) => {
      await queryClient.cancelQueries({ queryKey: ['comments'] })
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              commentIds.includes(comment.id)
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
      console.error('Ошибка при массовом архивировании комментариев:', err)
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для массового разархивирования комментариев
 */
export function useBulkUnarchive() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentIds: number[]) => api.bulkUnarchiveComments(commentIds),
    onMutate: async (commentIds) => {
      await queryClient.cancelQueries({ queryKey: ['comments'] })
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.map((comment: VKCommentResponse) =>
              commentIds.includes(comment.id)
                ? {
                    ...comment,
                    is_archived: false,
                    archived_at: undefined,
                  }
                : comment
            ),
          })),
        }
      })

      return { previousComments }
    },
    onError: (err, variables, context) => {
      console.error('Ошибка при массовом разархивировании комментариев:', err)
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}

/**
 * Хук для массового удаления комментариев
 */
export function useBulkDelete() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commentIds: number[]) => api.bulkDeleteComments(commentIds),
    onMutate: async (commentIds) => {
      await queryClient.cancelQueries({ queryKey: ['comments'] })
      const previousComments = queryClient.getQueryData([
        'comments',
        'infinite',
      ])

      queryClient.setQueryData(['comments', 'infinite'], (old: any) => {
        if (!old) return old

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            items: page.items.filter(
              (comment: VKCommentResponse) => !commentIds.includes(comment.id)
            ),
          })),
        }
      })

      return { previousComments }
    },
    onError: (err, variables, context) => {
      console.error('Ошибка при массовом удалении комментариев:', err)
      if (context?.previousComments) {
        queryClient.setQueryData(
          ['comments', 'infinite'],
          context.previousComments
        )
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['comments'] })
    },
  })
}
