/**
 * API клиент для взаимодействия с backend
 */

// В Docker окружении используем относительные URL,
// которые будут обрабатываться Nginx reverse proxy
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

// Import types
import type {
  Comment as VKComment,
  CommentsResponse,
  CommentFilters,
  UpdateCommentRequest,
} from '@/entities/comment'
import type { GlobalStats, DashboardStats } from '@/entities/dashboard'
import type {
  VKGroup,
  GroupsResponse,
  CreateGroupRequest,
  UpdateGroupRequest,
  GroupsFilters,
  GroupStats,
  GroupsStats,
  GroupBulkAction,
  GroupBulkResponse,
  UploadGroupsResponse,
  UploadProgress,
} from '@/entities/groups'
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
  ParseStatus,
  StopParseRequest,
  StopParseResponse,
} from '@/entities/parser'

export class ApiClient {
  private baseURL: string

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    // Retry логика для обработки временных ошибок
    const maxRetries = 3
    let lastError: Error | null = null

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        const response = await fetch(url, config)

        if (!response.ok) {
          // Для ошибок 503 и 429 делаем retry
          if ((response.status === 503 || response.status === 429) && attempt < maxRetries - 1) {
            const delay = Math.pow(2, attempt) * 1000 // Exponential backoff: 1s, 2s, 4s
            await new Promise(resolve => setTimeout(resolve, delay))
            continue
          }

          let errorMessage = `HTTP error! status: ${response.status}`

          try {
            const errorData = await response.json()
            // Backend может возвращать ошибки в формате { error: { message: string } }
            if (errorData.error?.message) {
              errorMessage = errorData.error.message
            } else if (errorData.message) {
              errorMessage = errorData.message
            } else if (errorData.detail) {
              errorMessage = errorData.detail
            }
          } catch {
            // Если не удается распарсить JSON, используем стандартное сообщение
          }

          throw new Error(errorMessage)
        }

        // Для некоторых endpoints может не быть тела ответа
        if (response.status === 204) {
          return undefined as T
        }

        return await response.json()
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error occurred')

        // Если это не сетевая ошибка или последняя попытка, прерываем retry
        if (attempt === maxRetries - 1 || !this.isRetryableError(lastError)) {
          break
        }

        // Задержка перед следующей попыткой
        const delay = Math.pow(2, attempt) * 1000
        await new Promise(resolve => setTimeout(resolve, delay))
      }
    }

    throw lastError || new Error('Unknown error occurred')
  }

  private isRetryableError(error: Error): boolean {
    const message = error.message.toLowerCase()
    return (
      message.includes('network') ||
      message.includes('timeout') ||
      message.includes('fetch') ||
      message.includes('503') ||
      message.includes('429')
    )
  }

  async getComment(_id: number): Promise<VKComment> {
    // TODO: Endpoint не реализован на backend
    throw new Error('Endpoint not implemented')
  }

  async updateComment(_id: number, _data: UpdateCommentRequest): Promise<VKComment> {
    // TODO: Endpoint не реализован на backend
    throw new Error('Endpoint not implemented')
  }

  async deleteComment(_id: number): Promise<void> {
    // TODO: Endpoint не реализован на backend
    throw new Error('Endpoint not implemented')
  }

  // Stats API
  async getGlobalStats(): Promise<GlobalStats> {
    const backendStats = await this.request<Record<string, unknown>>('/api/v1/parser/stats')
    return this.adaptBackendStatsToGlobalStats(backendStats)
  }

  async getDashboardStats(): Promise<DashboardStats> {
    const backendStats = await this.request<Record<string, unknown>>('/api/v1/parser/stats')
    return this.adaptBackendStatsToDashboardStats(backendStats)
  }

  // Адаптеры для преобразования данных backend в формат frontend
  private adaptBackendStatsToGlobalStats(backendStats: Record<string, unknown>): GlobalStats {
    return {
      total_comments: Number(backendStats.total_comments_found) || 0,
      total_matches: Number(backendStats.completed_tasks) || 0,
      comments_with_keywords: Number(backendStats.running_tasks) || 0,
      active_groups: Number(backendStats.running_tasks) || 0,
      active_keywords: Number(backendStats.completed_tasks) || 0,
      total_groups: Number(backendStats.total_tasks) || 0,
      total_keywords: Number(backendStats.failed_tasks) || 0,
    }
  }

  private adaptBackendStatsToDashboardStats(backendStats: Record<string, unknown>): DashboardStats {
    return {
      today_comments: Number(backendStats.total_comments_found) || 0,
      today_matches: Number(backendStats.completed_tasks) || 0,
      week_comments: Number(backendStats.total_posts_found) || 0,
      week_matches: Number(backendStats.running_tasks) || 0,
      recent_activity: [],
      top_groups: [],
      top_keywords: [],
    }
  }

  // Groups API
  async getGroups(params?: GroupsFilters): Promise<GroupsResponse> {
    const queryParams = new URLSearchParams()
    if (params?.is_active !== undefined)
      queryParams.append('is_active', params.is_active.toString())
    if (params?.search) queryParams.append('search', params.search)
    if (params?.has_monitoring !== undefined)
      queryParams.append('has_monitoring', params.has_monitoring.toString())
    if (params?.min_members !== undefined)
      queryParams.append('min_members', params.min_members.toString())
    if (params?.max_members !== undefined)
      queryParams.append('max_members', params.max_members.toString())
    if (params?.page !== undefined) queryParams.append('page', params.page.toString())
    if (params?.size !== undefined) queryParams.append('size', params.size.toString())

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

  async getGroupStats(id: number): Promise<GroupStats> {
    return this.request(`/api/v1/groups/${id}/stats`)
  }

  async getGroupsOverviewStats(): Promise<GroupsStats> {
    return this.request('/api/v1/groups/stats/overview')
  }

  async searchGroups(q: string, params?: GroupsFilters): Promise<GroupsResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('q', q)
    if (params?.is_active !== undefined)
      queryParams.append('is_active', params.is_active.toString())
    if (params?.page !== undefined) queryParams.append('page', params.page.toString())
    if (params?.size !== undefined) queryParams.append('size', params.size.toString())

    return this.request(`/api/v1/groups/search/?${queryParams.toString()}`)
  }

  async activateGroup(id: number): Promise<VKGroup> {
    return this.request(`/api/v1/groups/${id}/activate`, {
      method: 'POST',
    })
  }

  async deactivateGroup(id: number): Promise<VKGroup> {
    return this.request(`/api/v1/groups/${id}/deactivate`, {
      method: 'POST',
    })
  }

  async bulkActivateGroups(actionData: GroupBulkAction): Promise<GroupBulkResponse> {
    return this.request('/api/v1/groups/bulk/activate', {
      method: 'POST',
      body: JSON.stringify(actionData),
    })
  }

  async bulkDeactivateGroups(actionData: GroupBulkAction): Promise<GroupBulkResponse> {
    return this.request('/api/v1/groups/bulk/deactivate', {
      method: 'POST',
      body: JSON.stringify(actionData),
    })
  }

  async getGroupByVkId(vkId: number): Promise<VKGroup> {
    return this.request(`/api/v1/groups/vk/${vkId}`)
  }

  async getGroupByScreenName(screenName: string): Promise<VKGroup> {
    return this.request(`/api/v1/groups/screen/${screenName}`)
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
    if (params?.page !== undefined) queryParams.append('page', params.page.toString())
    if (params?.size !== undefined) queryParams.append('size', params.size.toString())
    if (params?.active_only !== undefined)
      queryParams.append('active_only', params.active_only.toString())
    if (params?.category) queryParams.append('category', params.category)
    if (params?.priority_min !== undefined)
      queryParams.append('priority_min', params.priority_min.toString())
    if (params?.priority_max !== undefined)
      queryParams.append('priority_max', params.priority_max.toString())
    if (params?.match_count_min !== undefined)
      queryParams.append('match_count_min', params.match_count_min.toString())
    if (params?.match_count_max !== undefined)
      queryParams.append('match_count_max', params.match_count_max.toString())

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

  async updateKeyword(id: number, updates: UpdateKeywordRequest): Promise<Keyword> {
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

  async getKeywordStats(id: number): Promise<KeywordStats> {
    return this.request(`/api/v1/keywords/${id}/stats`)
  }

  async searchKeywords(searchRequest: KeywordsSearchRequest): Promise<KeywordsResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('query', searchRequest.query)
    if (searchRequest.active_only !== undefined)
      queryParams.append('active_only', searchRequest.active_only.toString())
    if (searchRequest.category) queryParams.append('category', searchRequest.category)
    if (searchRequest.limit !== undefined)
      queryParams.append('limit', searchRequest.limit.toString())
    if (searchRequest.offset !== undefined)
      queryParams.append('offset', searchRequest.offset.toString())

    return this.request(`/api/v1/keywords/search?${queryParams.toString()}`)
  }

  async getKeywordsCategories(): Promise<KeywordCategoriesResponse> {
    return this.request('/api/v1/keywords/categories')
  }

  async bulkActivateKeywords(actionData: KeywordBulkAction): Promise<KeywordBulkResponse> {
    return this.request('/api/v1/keywords/bulk/activate', {
      method: 'POST',
      body: JSON.stringify(actionData),
    })
  }

  async bulkDeactivateKeywords(actionData: KeywordBulkAction): Promise<KeywordBulkResponse> {
    return this.request('/api/v1/keywords/bulk/deactivate', {
      method: 'POST',
      body: JSON.stringify(actionData),
    })
  }

  async bulkArchiveKeywords(actionData: KeywordBulkAction): Promise<KeywordBulkResponse> {
    return this.request('/api/v1/keywords/bulk/archive', {
      method: 'POST',
      body: JSON.stringify(actionData),
    })
  }

  async bulkDeleteKeywords(actionData: KeywordBulkAction): Promise<KeywordBulkResponse> {
    return this.request('/api/v1/keywords/bulk/delete', {
      method: 'POST',
      body: JSON.stringify(actionData),
    })
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

  async startBulkParser(bulkData: StartBulkParserForm): Promise<BulkParseResponse> {
    return this.request<BulkParseResponse>('/api/v1/parser/parse', {
      method: 'POST',
      body: JSON.stringify(bulkData),
    })
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

  async getParserTasks(filters?: ParserTaskFilters): Promise<ParserTasksResponse> {
    const queryParams = new URLSearchParams()
    if (filters?.page !== undefined) queryParams.append('page', filters.page.toString())
    if (filters?.size !== undefined) queryParams.append('size', filters.size.toString())
    if (filters?.status) queryParams.append('status', filters.status)
    if (filters?.group_id !== undefined) queryParams.append('group_id', filters.group_id.toString())
    if (filters?.date_from) queryParams.append('date_from', filters.date_from)
    if (filters?.date_to) queryParams.append('date_to', filters.date_to)

    const queryString = queryParams.toString()
    const endpoint = `/api/v1/parser/tasks${queryString ? `?${queryString}` : ''}`

    return this.request(endpoint)
  }

  async getParserTask(taskId: string): Promise<ParseStatus> {
    return this.request(`/api/v1/parser/tasks/${taskId}`)
  }

  async stopParser(request: StopParseRequest = {}): Promise<StopParseResponse> {
    const body = Object.keys(request).length > 0 ? request : null
    return this.request('/api/v1/parser/stop', {
      method: 'POST',
      body: body ? JSON.stringify(body) : null,
    })
  }

  async getParserHistory(page = 1, size = 10): Promise<ParserHistoryResponse> {
    const queryParams = new URLSearchParams()
    queryParams.append('page', page.toString())
    queryParams.append('size', size.toString())

    return this.request(`/api/v1/parser/tasks?${queryParams.toString()}`)
  }

  // Comments API (Parser related)
  async getComments(filters?: CommentFilters): Promise<CommentsResponse> {
    const queryParams = new URLSearchParams()
    if (filters?.page !== undefined) queryParams.append('page', filters.page.toString())
    if (filters?.size !== undefined) queryParams.append('size', filters.size.toString())

    // Всегда используем search endpoint для гибкости поиска
    const endpoint = '/api/v1/comments/search'

    if (filters?.text) {
      // Если есть текстовый поиск
      queryParams.append('q', filters.text)
    } else if (filters?.group_id !== undefined) {
      // Если указана группа - добавляем её как дополнительный фильтр
      queryParams.append('q', '  ') // Минимальная длина для валидации
      queryParams.append('group_id', filters.group_id.toString())
    } else if (filters?.post_id !== undefined) {
      // Если указан пост - добавляем его как дополнительный фильтр
      queryParams.append('q', '  ') // Минимальная длина для валидации
      queryParams.append('post_id', filters.post_id.toString())
    } else {
      // Если нет параметров - ищем все комментарии
      queryParams.append('q', '  ') // Минимальная длина для валидации
    }

    // Добавляем дополнительные фильтры
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
    const fullEndpoint = `${endpoint}${queryString ? `?${queryString}` : ''}`

    return this.request(fullEndpoint)
  }

  async getCommentWithKeywords(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/comments/${commentId}`)
  }

  async updateCommentStatus(
    commentId: number,
    statusUpdate: UpdateCommentRequest
  ): Promise<VKComment> {
    return this.request(`/api/v1/comments/${commentId}`, {
      method: 'PUT',
      body: JSON.stringify(statusUpdate),
    })
  }

  async markCommentViewed(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/comments/${commentId}/view`, {
      method: 'POST',
    })
  }

  async archiveComment(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/comments/${commentId}/archive`, {
      method: 'POST',
    })
  }

  async unarchiveComment(commentId: number): Promise<VKComment> {
    return this.request(`/api/v1/comments/${commentId}/unarchive`, {
      method: 'POST',
    })
  }

  // Health check
  async healthCheck(): Promise<{ success: boolean; message: string }> {
    return this.request('/api/v1/health')
  }

  async detailedHealthCheck(): Promise<Record<string, unknown>> {
    return this.request('/api/v1/health/detailed')
  }

  async readinessCheck(): Promise<Record<string, unknown>> {
    return this.request('/api/v1/health/ready')
  }

  async livenessCheck(): Promise<Record<string, unknown>> {
    return this.request('/api/v1/health/live')
  }

  async systemStatus(): Promise<Record<string, unknown>> {
    return this.request('/api/v1/health/status')
  }
}

export const apiClient = new ApiClient()
