import { useState, useEffect } from 'react'

import { apiClient } from '@/shared/lib'

import {
  Keyword,
  KeywordsResponse,
  CreateKeywordRequest,
  UpdateKeywordRequest,
  KeywordsFilters,
  KeywordStats,
  UploadKeywordsResponse,
} from './types'

export const useKeywords = (filters?: KeywordsFilters) => {
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchKeywords = async () => {
    setLoading(true)
    setError(null)
    try {
      const params: any = {}

      if (filters?.active_only !== undefined) {
        params.active_only = filters.active_only
      }
      if (filters?.category) {
        params.category = filters.category
      }
      if (filters?.search) {
        params.q = filters.search
      }

      const response: KeywordsResponse = await apiClient.getKeywords(params)
      setKeywords(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keywords')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKeywords()
  }, [filters?.active_only, filters?.category, filters?.search])

  const createKeyword = async (keywordData: CreateKeywordRequest): Promise<Keyword> => {
    try {
      const newKeyword: Keyword = await apiClient.createKeyword(keywordData)
      setKeywords(prev => [newKeyword, ...prev])
      return newKeyword
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create keyword')
    }
  }

  const updateKeyword = async (id: number, updates: UpdateKeywordRequest): Promise<Keyword> => {
    try {
      const updatedKeyword: Keyword = await apiClient.updateKeyword(id, updates)
      setKeywords(prev => prev.map(keyword => (keyword.id === id ? updatedKeyword : keyword)))
      return updatedKeyword
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update keyword')
    }
  }

  const deleteKeyword = async (id: number): Promise<void> => {
    try {
      await apiClient.deleteKeyword(id)
      setKeywords(prev => prev.filter(keyword => keyword.id !== id))
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to delete keyword')
    }
  }

  const toggleKeywordStatus = async (id: number, isActive: boolean): Promise<Keyword> => {
    return updateKeyword(id, { is_active: isActive })
  }

  return {
    keywords,
    loading,
    error,
    createKeyword,
    updateKeyword,
    deleteKeyword,
    toggleKeywordStatus,
    refetch: fetchKeywords,
  }
}

export const useKeyword = (id: number) => {
  const [keyword, setKeyword] = useState<Keyword | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchKeyword = async () => {
    if (!id) return

    setLoading(true)
    setError(null)
    try {
      const data: Keyword = await apiClient.getKeyword(id)
      setKeyword(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keyword')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchKeyword()
  }, [id])

  return {
    keyword,
    loading,
    error,
    refetch: fetchKeyword,
  }
}

export const useKeywordStats = (id: number) => {
  const [stats, setStats] = useState<KeywordStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    if (!id) return

    setLoading(true)
    setError(null)
    try {
      const data: KeywordStats = await apiClient.getKeywordStats(id)
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keyword stats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [id])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

export const useUploadKeywords = () => {
  const [uploadProgress, setUploadProgress] = useState<any | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const uploadKeywords = async (file: File, category?: string): Promise<UploadKeywordsResponse> => {
    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      if (category) {
        formData.append('category', category)
      }

      const result: UploadKeywordsResponse = await apiClient.uploadKeywords(formData)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload keywords')
      throw err
    } finally {
      setUploading(false)
    }
  }

  const getUploadProgress = async (uploadId: string): Promise<any> => {
    try {
      const progress: any = await apiClient.getKeywordsUploadProgress(uploadId)
      setUploadProgress(progress)
      return progress
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to get upload progress')
    }
  }

  return {
    uploadKeywords,
    getUploadProgress,
    uploadProgress,
    uploading,
    error,
  }
}
