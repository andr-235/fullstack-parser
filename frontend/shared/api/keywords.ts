/**
 * API для работы с ключевыми словами
 */

import { httpClient } from '@/shared/lib/http-client'
import type {
  Keyword,
  KeywordsResponse,
  CreateKeywordRequest,
  UpdateKeywordRequest,
  KeywordsFilters,
  KeywordsSearchRequest,
  KeywordStats,
  KeywordCategoriesResponse,
  KeywordBulkAction,
  KeywordBulkResponse,
  UploadKeywordsResponse,
} from '@/entities/keywords'

export const keywordsApi = {
  async getKeywords(params?: KeywordsFilters): Promise<KeywordsResponse> {
    return httpClient.get('/api/v1/keywords', params)
  },

  async createKeyword(keywordData: CreateKeywordRequest): Promise<Keyword> {
    return httpClient.post('/api/v1/keywords', keywordData)
  },

  async updateKeyword(id: number, updates: UpdateKeywordRequest): Promise<Keyword> {
    return httpClient.patch(`/api/v1/keywords/${id}`, updates)
  },

  async deleteKeyword(id: number): Promise<void> {
    return httpClient.delete(`/api/v1/keywords/${id}`)
  },

  async getKeyword(id: number): Promise<Keyword> {
    return httpClient.get(`/api/v1/keywords/${id}`)
  },

  async searchKeywords(searchData: KeywordsSearchRequest): Promise<KeywordsResponse> {
    return httpClient.post('/api/v1/keywords/search', searchData)
  },

  async getKeywordStats(id: number): Promise<KeywordStats> {
    return httpClient.get(`/api/v1/keywords/${id}/stats`)
  },

  async getKeywordCategories(): Promise<KeywordCategoriesResponse> {
    return httpClient.get('/api/v1/keywords/categories')
  },

  async bulkAction(action: KeywordBulkAction): Promise<KeywordBulkResponse> {
    return httpClient.post('/api/v1/keywords/bulk', action)
  },

  async uploadKeywords(file: File): Promise<UploadKeywordsResponse> {
    const formData = new FormData()
    formData.append('file', file)

    return httpClient.post('/api/v1/keywords/upload', formData)
  },
}
