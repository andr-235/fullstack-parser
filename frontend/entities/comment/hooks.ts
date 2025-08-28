import { useState, useEffect } from 'react'
import {
  Comment,
  CreateCommentRequest,
  UpdateCommentRequest,
  CommentFilters,
} from './types'

export const useComments = (filters?: CommentFilters) => {
  const [comments, setComments] = useState<Comment[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchComments = async () => {
    setLoading(true)
    setError(null)
    try {
      // TODO: Implement API call
      const response = await fetch('/api/comments')
      const data = await response.json()
      setComments(data)
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
      const response = await fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(comment),
      })
      const newComment = await response.json()
      setComments((prev) => [...prev, newComment])
      return newComment
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to create comment'
      )
    }
  }

  const updateComment = async (id: string, updates: UpdateCommentRequest) => {
    try {
      const response = await fetch(`/api/comments/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      })
      const updatedComment = await response.json()
      setComments((prev) =>
        prev.map((comment) => (comment.id === id ? updatedComment : comment))
      )
      return updatedComment
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to update comment'
      )
    }
  }

  const deleteComment = async (id: string) => {
    try {
      await fetch(`/api/comments/${id}`, { method: 'DELETE' })
      setComments((prev) => prev.filter((comment) => comment.id !== id))
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to delete comment'
      )
    }
  }

  return {
    comments,
    loading,
    error,
    createComment,
    updateComment,
    deleteComment,
    refetch: fetchComments,
  }
}
