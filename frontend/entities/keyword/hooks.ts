import { useState } from 'react'
import { Keyword, CreateKeywordRequest, UpdateKeywordRequest } from './types'

export const useKeywords = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchKeywords = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/keywords')
      const data = await response.json()
      setKeywords(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keywords')
    } finally {
      setLoading(false)
    }
  }

  const createKeyword = async (keywordData: CreateKeywordRequest) => {
    try {
      const response = await fetch('/api/keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keywordData),
      })
      const newKeyword = await response.json()
      setKeywords((prev) => [...prev, newKeyword])
      return newKeyword
    } catch (err) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to create keyword'
      )
    }
  }

  return {
    keywords,
    loading,
    error,
    fetchKeywords,
    createKeyword,
  }
}
