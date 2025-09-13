import { useState, useEffect, useCallback, useRef } from 'react'

import { httpClient } from '@/shared/lib'

import { Comment, CommentFilters, CommentsResponse } from '../types'

// Типы для обработки ошибок API
interface ApiError {
  message?: string
  detail?: string
  error?: {
    message?: string
  }
}

// Вспомогательная функция для обработки ошибок
function getErrorMessage(err: unknown, defaultMessage: string): string {
  if (err instanceof Error) {
    return err.message
  }

  if (typeof err === 'string') {
    return err
  }

  if (typeof err === 'object' && err !== null) {
    const apiError = err as ApiError
    if (apiError.message) {
      return apiError.message
    }
    if (apiError.detail) {
      return apiError.detail
    }
    if (apiError.error?.message) {
      return apiError.error.message
    }
    return `API Error: ${JSON.stringify(apiError)}`
  }

  return defaultMessage
}

export const useInfiniteComments = (filters?: CommentFilters) => {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)

  const pageSize = 20
  const isLoadingRef = useRef(false)

  const fetchComments = useCallback(
    async (page: number = 1, reset: boolean = false) => {
      if (isLoadingRef.current) return

      isLoadingRef.current = true

      if (reset) {
        setLoading(true)
        setComments([])
        setCurrentPage(1)
        setHasMore(true)
      } else {
        setLoadingMore(true)
      }

      setError(null)

      try {
        const params: Record<string, unknown> = {
          page,
          size: pageSize,
        }

        if (filters?.is_viewed !== undefined) params.is_viewed = filters.is_viewed
        if (filters?.group_id) params.group_id = filters.group_id
        if (filters?.keyword_id) params.keyword_id = filters.keyword_id
        if (filters?.has_keywords !== undefined) params.has_keywords = filters.has_keywords

        // Если нет фильтров, используем поиск для получения всех комментариев
        if (!filters?.group_id && !filters?.text && !filters?.has_keywords) {
          params.text = '**' // Специальный запрос для получения всех комментариев
        }

        const response: CommentsResponse = await httpClient.get('/api/comments', { params })

        if (reset) {
          setComments(response.items)
        } else {
          setComments(prev => [...prev, ...response.items])
        }

        setTotalCount(response.total)
        setCurrentPage(page)
        setHasMore(response.items.length === pageSize && response.items.length > 0)
      } catch (err) {
        const errorMessage = getErrorMessage(err, 'Failed to fetch comments')
        setError(errorMessage)
      } finally {
        setLoading(false)
        setLoadingMore(false)
        isLoadingRef.current = false
      }
    },
    [filters, pageSize]
  )

  const loadMore = useCallback(() => {
    if (!loadingMore && hasMore && !isLoadingRef.current) {
      fetchComments(currentPage + 1, false)
    }
  }, [fetchComments, currentPage, loadingMore, hasMore])

  const refetch = useCallback(() => {
    fetchComments(1, true)
  }, [fetchComments])

  useEffect(() => {
    fetchComments(1, true)
  }, [fetchComments])

  return {
    comments,
    loading,
    loadingMore,
    error,
    hasMore,
    totalCount,
    loadMore,
    refetch,
  }
}
