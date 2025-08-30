/**
 * API клиент для взаимодействия с backend
 */

// В Docker окружении используем относительные URL,
// которые будут обрабатываться Nginx reverse proxy
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

// Import types
import type { GlobalStats, DashboardStats } from '@/entities/dashboard'
import type {
  VKGroup,
  GroupsResponse,
  CreateGroupRequest,
  UpdateGroupRequest,
  GroupsFilters,
  UploadGroupsResponse,
  UploadProgress,
} from '@/entities/groups'
import type {
  Keyword,
  KeywordsResponse,
  CreateKeywordRequest,
  UpdateKeywordRequest,
  KeywordsFilters,
  UploadKeywordsResponse,
} from '@/entities/keywords'
import type {
  Comment as VKComment,
  CommentsResponse,
  CommentFilters,
  UpdateCommentRequest,
} from '@/entities/comment'
import type {
  ParseTaskCreate,
  ParseTaskResponse,
  ParserState,
  ParserStats,
  ParserGlobalStats,
  ParserTasksResponse,
  ParserHistoryResponse,
  ParserTaskFilters,
  StartBulkParserForm,
  BulkParseResponse,
} from '@/entities/parser'

export class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(
          errorData.message || `HTTP error! status: ${response.status}`
        )
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  async getComment(id: number): Promise<VKComment> {
    // TODO: Endpoint не реализован на backend
    console.warn(`getComment(${id}): Endpoint not implemented on backend yet`)
    throw new Error('Endpoint not implemented')
  }

  async updateComment(
    id: number,
    data: UpdateCommentRequest
  ): Promise<VKComment> {
    // TODO: Endpoint не реализован на backend
    console.warn(
      `updateComment(${id}): Endpoint not implemented on backend yet`
    )
    throw new Error('Endpoint not implemented')
  }

  async deleteComment(id: number): Promise<void> {
    // TODO: Endpoint не реализован на backend
    console.warn(
      `deleteComment(${id}): Endpoint not implemented on backend yet`
    )
    throw new Error('Endpoint not implemented')
  }

  // Stats API
  async getGlobalStats(): Promise<GlobalStats> {
    return this.request('/api/v1/stats/global')
  }

  async getDashboardStats(): Promise<DashboardStats> {
    return this.request('/api/v1/stats/dashboard')
  }

  // Groups API
  async getGroups(params?: GroupsFilters): Promise<GroupsResponse> {
    const queryParams = new URLSearchParams()
    if (params?.active_only !== undefined)
      queryParams.append('active_only', params.active_only.toString())
    if (params?.search) queryParams.append('search', params.search)
    if (params?.page !== undefined)
      queryParams.append('page', params.page.toString())
    if (params?.size !== undefined)
      queryParams.append('size', params.size.toString())

    const queryString = queryParams.toString()
    const endpoint = `/api/v1/groups${queryString ? `?${queryString}` : ''}`

    return this.request(endpoint)
  }

  async createGroup(groupData: CreateGroupRequest): Promise<VKGroup> {
    return this.request('/api/v1/groups', {
      method: 'POST',
      body: JSON.stringify(groupData),
    })
  }

  async updateGroup(id: number, updates: UpdateGroupRequest): Promise<VKGroup> {
    return this.request(`/api/v1/groups/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  }

  async deleteGroup(id: number): Promise<void> {
    return this.request(`/api/v1/groups/${id}`, {
      method: 'DELETE',
    })
  }

  async getGroup(id: number): Promise<VKGroup> {
    return this.request(`/api/v1/groups/${id}`)
  }

  async getGroupStats(id: number): Promise<any> {
    return this.request(`/api/v1/groups/${id}/stats`)
  }

  async uploadGroups(formData: FormData): Promise<UploadGroupsResponse> {
    const config: RequestInit = {
      method: 'POST',
      body: formData,
      // Не устанавливаем Content-Type для FormData - браузер сам установит с boundary
    }

    return this.request('/api/v1/groups/upload', config)
  }

  // Keywords API
  async getKeywords(params?: KeywordsFilters): Promise<KeywordsResponse> {
    const queryParams = new URLSearchParams()
    if (params?.page !== undefined)
      queryParams.append('page', params.page.toString())
    if (params?.size !== undefined)
      queryParams.append('size', params.size.toString())
    if (params?.active_only !== undefined)
      queryParams.append('active_only', params.active_only.toString())
    if (params?.category) queryParams.append('category', params.category)
    if (params?.search) queryParams.append('q', params.search)

    const queryString = queryParams.toString()
    const endpoint = `/api/v1/keywords${queryString ? `?${queryString}` : ''}`

    return this.request(endpoint)
  }

  async createKeyword(keywordData: CreateKeywordRequest): Promise<Keyword> {
    return this.request('/api/v1/keywords', {
      method: 'POST',
      body: JSON.stringify(keywordData),
    })
  }

  async updateKeyword(
    id: number,
    updates: UpdateKeywordRequest
  ): Promise<Keyword> {
    return this.request(`/api/v1/keywords/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  }

  async deleteKeyword(id: number): Promise<void> {
    return this.request(`/api/v1/keywords/${id}`, {
      method: 'DELETE',
    })
  }

  async getKeyword(id: number): Promise<Keyword> {
    return this.request(`/api/v1/keywords/${id}`)
  }

  async getKeywordStats(id: number): Promise<any> {
    return this.request(`/api/v1/keywords/${id}/stats`)
  }

  async uploadKeywords(formData: FormData): Promise<UploadKeywordsResponse> {
    const config: RequestInit = {
      method: 'POST',
      body: formData,
      // Не устанавливаем Content-Type для FormData - браузер сам установит с boundary
    }

    return this.request('/api/v1/keywords/upload', config)
  }

  async getKeywordsUploadProgress(uploadId: string): Promise<UploadProgress> {
    return this.request(`/api/v1/keywords/upload-progress/${uploadId}`)
  }

  // Parser API
  async startParser(taskData: ParseTaskCreate): Promise<ParseTaskResponse> {
    return this.request('/api/v1/parser/parse', {
      method: 'POST',
      body: JSON.stringify(taskData),
    })
  }

  async startBulkParser(
    bulkData: StartBulkParserForm
  ): Promise<BulkParseResponse> {
    console.log('API: Starting bulk parser with data:', bulkData)
    const result = await this.request<BulkParseResponse>(
      '/api/v1/parser/parse/bulk',
      {
        method: 'POST',
        body: JSON.stringify(bulkData),
      }
    )
    console.log('API: Bulk parser response:', result)
    return result
  }

  async getParserState(): Promise<ParserState> {
    return this.request('/api/v1/parser/state')
  }

  async getParserStats(): Promise<ParserStats> {
    return this.request('/api/v1/parser/stats')
  }

  async getParserGlobalStats(): Promise<ParserGlobalStats> {
    return this.request('/api/v1/parser/stats/global')
  }

  async getParserTasks(
    filters?: ParserTaskFilters
  ): Promise<ParserTasksResponse> {
    const queryParams = new URLSearchParams()
    if (filters?.page !== undefined)
      queryParams.append('page', filters.page.toString())
    if (filters?.size !== undefined)
      queryParams.append('size', filters.size.toString())
    if (filters?.status) queryParams.append('status', filters.status)
    if (filters?.group_id !== undefined)
      queryParams.append('group_id', filters.group_id.toString())
    if (filters?.date_from) queryParams.append('date_from', filters.date_from)
    if (filters?.date_to) queryParams.append('date_to', filters.date_to)

    const queryString = queryParams.toString()
    const endpoint = `/api/v1/parser/tasks${queryString ? `?${queryString}` : ''}`

    return this.request(endpoint)
  }

  async stopParser(): Promise<{ status: string; message: string }> {
    return this.request('/api/v1/parser/stop', {
      method: 'POST',
    })
  }

  async getParserHistory(skip = 0, limit = 10): Promise<ParserHistoryResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('skip', skip.toString())
    queryParams.append('limit', limit.toString())

    return this.request(`/api/v1/parser/history?${queryParams.toString()}`)
  }

  // Comments API (Parser related)
  async getComments(filters?: CommentFilters): Promise<CommentsResponse> {
    const queryParams = new URLSearchParams()
    if (filters?.page !== undefined)
      queryParams.append('page', filters.page.toString())
    if (filters?.size !== undefined)
      queryParams.append('size', filters.size.toString())
    if (filters?.text) queryParams.append('text', filters.text)
    if (filters?.group_id !== undefined)
      queryParams.append('group_id', filters.group_id.toString())
    if (filters?.keyword_id !== undefined)
      queryParams.append('keyword_id', filters.keyword_id.toString())
    if (filters?.authorId !== undefined)
      queryParams.append('author_id', filters.authorId.toString())
    if (filters?.date_from) queryParams.append('date_from', filters.date_from)
    if (filters?.date_to) queryParams.append('date_to', filters.date_to)
    if (filters?.is_viewed !== undefined)
      queryParams.append('is_viewed', filters.is_viewed.toString())
    if (filters?.is_archived !== undefined)
      queryParams.append('is_archived', filters.is_archived.toString())

    const queryString = queryParams.toString()
    const endpoint = `/api/v1/parser/comments${queryString ? `?${queryString}` : ''}`

    return this.request(endpoint)
  }

  async getCommentWithKeywords(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/parser/comments/${commentId}`)
  }

  async updateCommentStatus(
    commentId: number,
    statusUpdate: UpdateCommentRequest
  ): Promise<VKComment> {
    return this.request(`/api/v1/parser/comments/${commentId}/status`, {
      method: 'PUT',
      body: JSON.stringify(statusUpdate),
    })
  }

  async markCommentViewed(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/parser/comments/${commentId}/view`, {
      method: 'POST',
    })
  }

  async archiveComment(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/parser/comments/${commentId}/archive`, {
      method: 'POST',
    })
  }

  async unarchiveComment(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/parser/comments/${commentId}/unarchive`, {
      method: 'POST',
    })
  }

  // Health check
  async healthCheck(): Promise<{ success: boolean; message: string }> {
    return this.request('/api/v1/health')
  }
}

export const apiClient = new ApiClient()
