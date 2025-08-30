import { useState, useEffect } from 'react'
import { apiClient } from '@/shared/lib/index'
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

  const fetchComments = async () => {
    setLoading(true)
    setError(null)
    try {
      const params: any = {}

      if (filters?.is_viewed !== undefined) params.is_viewed = filters.is_viewed
      if (filters?.group_id) params.group_id = filters.group_id
      if (filters?.keyword_id) params.keyword_id = filters.keyword_id

      const response: CommentsResponse = await apiClient.getComments(params)
      setComments(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch comments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchComments()
  }, [filters])

  const createComment = async (comment: CreateCommentRequest) => {
    try {
      // Note: Backend doesn't support creating comments via API
      // This is for future use or if you add this functionality
      throw new Error('Creating comments is not supported via API')
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create comment')
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
      throw new Error(err instanceof Error ? err.message : 'Failed to update comment')
    }
  }

  const deleteComment = async (id: string) => {
    try {
      await apiClient.deleteComment(parseInt(id))
      setComments(prev => prev.filter(comment => comment.id !== parseInt(id)))
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to delete comment')
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
      throw new Error(err instanceof Error ? err.message : 'Failed to mark comment as viewed')
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
