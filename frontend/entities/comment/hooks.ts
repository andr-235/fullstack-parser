import { useState, useEffect, useCallback } from 'react'

import { apiClient } from '@/shared/lib'

import {
  Comment,
  CreateCommentRequest,
  UpdateCommentRequest,
  CommentFilters,
  CommentsResponse,
} from './types'

export const useComments = (filters?: CommentFilters) => {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchComments = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: Record<string, unknown> = {}

      if (filters?.is_viewed !== undefined) params.is_viewed = filters.is_viewed
      if (filters?.group_id) params.group_id = filters.group_id
      if (filters?.keyword_id) params.keyword_id = filters.keyword_id

      const response: CommentsResponse = await apiClient.getComments(params)
      setComments(response.items)
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : typeof err === 'string'
            ? err
            : 'Failed to fetch comments'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    fetchComments()
  }, [fetchComments])

  const createComment = async (_comment: CreateCommentRequest) => {
    try {
      // Note: Backend doesn't support creating comments via API
      // This is for future use or if you add this functionality
      throw new Error('Creating comments is not supported via API')
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : typeof err === 'string'
            ? err
            : 'Failed to create comment'
      throw new Error(errorMessage)
    }
  }

  const updateComment = async (id: string, updates: UpdateCommentRequest) => {
    try {
      const updatedComment = await apiClient.updateComment(parseInt(id), updates)
      setComments(prev =>
        prev.map(comment => (comment.id === parseInt(id) ? updatedComment : comment))
      )
      return updatedComment
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : typeof err === 'string'
            ? err
            : 'Failed to update comment'
      throw new Error(errorMessage)
    }
  }

  const deleteComment = async (id: string) => {
    try {
      await apiClient.deleteComment(parseInt(id))
      setComments(prev => prev.filter(comment => comment.id !== parseInt(id)))
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : typeof err === 'string'
            ? err
            : 'Failed to delete comment'
      throw new Error(errorMessage)
    }
  }

  const markAsViewed = async (id: string) => {
    try {
      await apiClient.markCommentViewed(parseInt(id))
      setComments(prev =>
        prev.map(comment =>
          comment.id === parseInt(id) ? { ...comment, is_viewed: true } : comment
        )
      )
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : typeof err === 'string'
            ? err
            : 'Failed to mark comment as viewed'
      throw new Error(errorMessage)
    }
  }

  return {
    comments,
    loading,
    error,
    createComment,
    updateComment,
    deleteComment,
    markAsViewed,
    refetch: fetchComments,
  }
}
