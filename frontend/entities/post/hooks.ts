import { useState } from 'react'

import { Post, CreatePostRequest, UpdatePostRequest } from './types'

export const usePosts = () => {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPosts = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/posts')
      const data = await response.json()
      setPosts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch posts')
    } finally {
      setLoading(false)
    }
  }

  const createPost = async (postData: CreatePostRequest) => {
    try {
      const response = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData),
      })
      const newPost = await response.json()
      setPosts(prev => [...prev, newPost])
      return newPost
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create post')
    }
  }

  return {
    posts,
    loading,
    error,
    fetchPosts,
    createPost,
  }
}
