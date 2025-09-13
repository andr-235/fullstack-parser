import { useState, useEffect, useCallback } from 'react'

import { httpClient } from '@/shared/lib'

import {
  Keyword,
  KeywordsResponse,
  CreateKeywordRequest,
  UpdateKeywordRequest,
  KeywordsFilters,
  KeywordStats,
  UploadKeywordsResponse,
  UploadProgress,
} from './types'

const KEYWORDS_CACHE_KEY = 'keywords-cache'
const CACHE_EXPIRY_KEY = 'keywords-cache-expiry'
const CACHE_DURATION = 5 * 60 * 1000 // 5 минут

interface CachedKeywords {
  data: Keyword[]
  timestamp: number
  filters: KeywordsFilters
}

export const useKeywords = (filters?: KeywordsFilters) => {
  const [keywords, setKeywords] = useState<Keyword[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Функции для работы с кэшем
  const getCachedKeywords = (): CachedKeywords | null => {
    try {
      const cached = localStorage.getItem(KEYWORDS_CACHE_KEY)
      const expiry = localStorage.getItem(CACHE_EXPIRY_KEY)

      if (!cached || !expiry) return null

      const now = Date.now()
      const cacheTime = parseInt(expiry, 10)

      if (now - cacheTime > CACHE_DURATION) {
        // Кэш устарел, очищаем
        localStorage.removeItem(KEYWORDS_CACHE_KEY)
        localStorage.removeItem(CACHE_EXPIRY_KEY)
        return null
      }

      return JSON.parse(cached)
    } catch {
      return null
    }
  }

  const setCachedKeywords = (data: Keyword[], filters?: KeywordsFilters) => {
    try {
      const cacheData: CachedKeywords = {
        data,
        timestamp: Date.now(),
        filters: filters || {},
      }
      localStorage.setItem(KEYWORDS_CACHE_KEY, JSON.stringify(cacheData))
      localStorage.setItem(CACHE_EXPIRY_KEY, Date.now().toString())
    } catch {
      // Игнорируем ошибки localStorage
    }
  }

  const isFiltersMatch = (
    cachedFilters: KeywordsFilters,
    currentFilters?: KeywordsFilters
  ): boolean => {
    if (!currentFilters) return true

    const keys = ['active_only', 'category', 'search'] as const
    return keys.every(key => {
      const cached = cachedFilters[key]
      const current = currentFilters[key]

      if (cached === undefined && current === undefined) return true
      if (cached === undefined || current === undefined) return false
      return cached === current
    })
  }

  const fetchKeywords = useCallback(
    async (forceRefresh = false) => {
      // Проверяем кэш, если не принудительное обновление
      if (!forceRefresh) {
        const cached = getCachedKeywords()
        if (cached && isFiltersMatch(cached.filters, filters)) {
          setKeywords(cached.data)
          return
        }
      }

      setLoading(true)
      setError(null)
      try {
        const params: Record<string, unknown> = {}

        if (filters?.active_only !== undefined) {
          params.active_only = filters.active_only
        }
        if (filters?.category) {
          params.category = filters.category
        }
        if (filters?.search) {
          params.q = filters.search
        }

        const response: KeywordsResponse = await httpClient.get('/api/keywords', { params })
        setKeywords(response.items)

        // Сохраняем в кэш
        setCachedKeywords(response.items, filters)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch keywords')
      } finally {
        setLoading(false)
      }
    },
    [filters]
  )

  useEffect(() => {
    fetchKeywords()
  }, [fetchKeywords])

  const createKeyword = async (keywordData: CreateKeywordRequest): Promise<Keyword> => {
    try {
      const newKeyword: Keyword = await httpClient.post('/api/keywords', keywordData)
      const updatedKeywords = [newKeyword, ...keywords]
      setKeywords(updatedKeywords)

      // Обновляем кэш
      setCachedKeywords(updatedKeywords, filters)

      return newKeyword
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create keyword')
    }
  }

  const updateKeyword = async (id: number, updates: UpdateKeywordRequest): Promise<Keyword> => {
    try {
      const updatedKeyword: Keyword = await httpClient.put(`/api/keywords/${id}`, updates)
      const updatedKeywords = keywords.map(keyword =>
        keyword.id === id ? updatedKeyword : keyword
      )
      setKeywords(updatedKeywords)

      // Обновляем кэш
      setCachedKeywords(updatedKeywords, filters)

      return updatedKeyword
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update keyword')
    }
  }

  const deleteKeyword = async (id: number): Promise<void> => {
    try {
      await httpClient.delete(`/api/keywords/${id}`)
      const updatedKeywords = keywords.filter(keyword => keyword.id !== id)
      setKeywords(updatedKeywords)

      // Обновляем кэш
      setCachedKeywords(updatedKeywords, filters)
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
    refetch: () => fetchKeywords(true), // Принудительное обновление
  }
}

export const useKeyword = (id: number) => {
  const [keyword, setKeyword] = useState<Keyword | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchKeyword = useCallback(async () => {
    if (!id) return

    setLoading(true)
    setError(null)
    try {
      const data: Keyword = await httpClient.get(`/api/keywords/${id}`)
      setKeyword(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keyword')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchKeyword()
  }, [fetchKeyword])

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

  const fetchStats = useCallback(async () => {
    if (!id) return

    setLoading(true)
    setError(null)
    try {
      const data: KeywordStats = await httpClient.get(`/api/keywords/${id}/stats`)
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch keyword stats')
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

export const useUploadKeywords = () => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
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

      const result: UploadKeywordsResponse = await httpClient.post('/api/keywords/upload', formData)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload keywords')
      throw err
    } finally {
      setUploading(false)
    }
  }

  const getUploadProgress = async (uploadId: string): Promise<UploadProgress> => {
    try {
      const progress: UploadProgress = await httpClient.get(`/api/keywords/upload-progress/${uploadId}`)
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
