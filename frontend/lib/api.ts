import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  VKGroupStats,
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
  KeywordUploadResponse,
  VKCommentResponse,
  CommentWithKeywords,
  CommentSearchParams,
  ParseTaskCreate,
  ParseTaskResponse,
  GlobalStats,
  DashboardStats,
  PaginatedResponse,
  StatusResponse,
  PaginationParams,
  APIError,
  ParserState,
  ParserStats,
  MonitoringStats,
  VKGroupMonitoring,
  MonitoringGroupUpdate,
  MonitoringRunResult,
} from '@/types/api'

/**
 * Конфигурация API клиента
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
if (!API_BASE_URL) {
  throw new Error(
    'NEXT_PUBLIC_API_URL не определён! Проверь .env и переменные окружения.'
  )
}

console.log('API_BASE_URL:', API_BASE_URL)

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Interceptors для обработки ошибок
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<APIError>) => {
        if (error.response?.data) {
          throw new Error(error.response.data.detail || 'API Error')
        }
        throw new Error(error.message || 'Network Error')
      }
    )
  }

  // VK Groups API
  async getGroups(params?: PaginationParams & { active_only?: boolean }) {
    const { data } = await this.client.get<PaginatedResponse<VKGroupResponse>>(
      '/groups/',
      {
        params,
      }
    )
    return data
  }

  async getGroup(groupId: number) {
    const { data } = await this.client.get<VKGroupResponse>(
      `/groups/${groupId}`
    )
    return data
  }

  async createGroup(groupData: VKGroupCreate) {
    const { data } = await this.client.post<VKGroupResponse>(
      '/groups/',
      groupData
    )
    return data
  }

  async updateGroup(groupId: number, updateData: VKGroupUpdate) {
    const { data } = await this.client.put<VKGroupResponse>(
      `/groups/${groupId}`,
      updateData
    )
    return data
  }

  async deleteGroup(groupId: number) {
    const { data } = await this.client.delete<StatusResponse>(
      `/groups/${groupId}`
    )
    return data
  }

  async getGroupStats(groupId: number) {
    const { data } = await this.client.get<VKGroupStats>(
      `/groups/${groupId}/stats`
    )
    return data
  }

  // Keywords API
  async getKeywords(
    params?: PaginationParams & {
      active_only?: boolean
      category?: string
      q?: string
    }
  ) {
    const { data } = await this.client.get<PaginatedResponse<KeywordResponse>>(
      '/keywords/',
      {
        params,
      }
    )
    return data
  }

  async getKeyword(keywordId: number) {
    const { data } = await this.client.get<KeywordResponse>(
      `/keywords/${keywordId}`
    )
    return data
  }

  async createKeyword(keywordData: KeywordCreate) {
    const { data } = await this.client.post<KeywordResponse>(
      '/keywords/',
      keywordData
    )
    return data
  }

  async updateKeyword(keywordId: number, updateData: KeywordUpdate) {
    const { data } = await this.client.put<KeywordResponse>(
      `/keywords/${keywordId}`,
      updateData
    )
    return data
  }

  async deleteKeyword(keywordId: number) {
    const { data } = await this.client.delete<StatusResponse>(
      `/keywords/${keywordId}`
    )
    return data
  }

  async createKeywordsBulk(keywordsData: KeywordCreate[]) {
    const { data } = await this.client.post<KeywordResponse[]>(
      '/keywords/bulk/',
      keywordsData
    )
    return data
  }

  async getKeywordCategories() {
    const { data } = await this.client.get<string[]>('/keywords/categories')
    return data
  }

  async uploadKeywordsFromFile(
    file: File,
    options?: {
      default_category?: string
      is_active?: boolean
      is_case_sensitive?: boolean
      is_whole_word?: boolean
    }
  ) {
    const formData = new FormData()
    formData.append('file', file)

    if (options?.default_category) {
      formData.append('default_category', options.default_category)
    }
    if (options?.is_active !== undefined) {
      formData.append('is_active', options.is_active.toString())
    }
    if (options?.is_case_sensitive !== undefined) {
      formData.append('is_case_sensitive', options.is_case_sensitive.toString())
    }
    if (options?.is_whole_word !== undefined) {
      formData.append('is_whole_word', options.is_whole_word.toString())
    }

    try {
      const { data } = await this.client.post<KeywordUploadResponse>(
        '/keywords/upload/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000, // Увеличиваем таймаут для загрузки файлов
          maxContentLength: 10 * 1024 * 1024, // 10MB
          maxBodyLength: 10 * 1024 * 1024, // 10MB
        }
      )
      return data
    } catch (error: any) {
      console.error('Upload error details:', error)

      // Улучшенная обработка ошибок
      if (error.code === 'ECONNABORTED') {
        throw new Error('Превышено время ожидания загрузки файла')
      }

      if (error.response?.status === 413) {
        throw new Error('Файл слишком большой. Максимальный размер: 5MB')
      }

      if (error.response?.status === 404) {
        throw new Error('Эндпоинт загрузки файлов недоступен')
      }

      if (error.response?.status === 500) {
        throw new Error('Ошибка сервера при обработке файла')
      }

      throw error
    }
  }

  // Comments API
  async getComments(params?: CommentSearchParams & PaginationParams) {
    const { data } = await this.client.get<
      PaginatedResponse<VKCommentResponse>
    >('/parser/comments', {
      params,
    })
    return data
  }

  async getCommentWithKeywords(commentId: number) {
    const { data } = await this.client.get<CommentWithKeywords>(
      `/parser/comments/${commentId}`
    )
    return data
  }

  // Parser API
  async startParser(taskData: ParseTaskCreate) {
    const { data } = await this.client.post<ParseTaskResponse>(
      '/parser/parse',
      taskData
    )
    return data
  }

  async getParserState() {
    const { data } = await this.client.get<ParserState>('/parser/state')
    return data
  }

  async getParserStats() {
    const { data } = await this.client.get<ParserStats>('/parser/stats')
    return data
  }

  async getRecentParseTasks(params?: PaginationParams) {
    const { data } = await this.client.get<
      PaginatedResponse<ParseTaskResponse>
    >('/parser/tasks', {
      params,
    })
    return data
  }

  async stopParser() {
    const { data } = await this.client.post<StatusResponse>('/parser/stop')
    return data
  }

  async getGlobalStats() {
    const { data } = await this.client.get<GlobalStats>('/stats/global')
    return data
  }

  // Dashboard API (предполагаемый endpoint)
  async getDashboardStats() {
    try {
      const { data } = await this.client.get<DashboardStats>('/stats/dashboard')
      return data
    } catch (error) {
      // Fallback к базовой статистике если нет дашборда
      const globalStats = await this.getGlobalStats()
      return {
        today_comments: 0,
        today_matches: 0,
        week_comments: globalStats.total_comments,
        week_matches: globalStats.comments_with_keywords,
        top_groups: [],
        top_keywords: [],
        recent_activity: [],
      } as DashboardStats
    }
  }

  // Health check
  async healthCheck() {
    try {
      const { data } = await this.client.get('/')
      return data
    } catch (error) {
      throw new Error('API недоступно')
    }
  }

  // Monitoring API
  async getMonitoringStats() {
    const { data } = await this.client.get<MonitoringStats>('/monitoring/stats')
    return data
  }

  async getMonitoringGroups(
    params?: PaginationParams & {
      active_only?: boolean
      monitoring_enabled?: boolean
    }
  ) {
    const { data } = await this.client.get<
      PaginatedResponse<VKGroupMonitoring>
    >('/monitoring/groups', { params })
    return data
  }

  async enableGroupMonitoring(
    groupId: number,
    intervalMinutes: number = 60,
    priority: number = 5
  ) {
    const { data } = await this.client.post<StatusResponse>(
      `/monitoring/groups/${groupId}/enable`,
      { interval_minutes: intervalMinutes, priority }
    )
    return data
  }

  async disableGroupMonitoring(groupId: number) {
    const { data } = await this.client.post<StatusResponse>(
      `/monitoring/groups/${groupId}/disable`
    )
    return data
  }

  async updateGroupMonitoring(
    groupId: number,
    updateData: MonitoringGroupUpdate
  ) {
    const { data } = await this.client.put<StatusResponse>(
      `/monitoring/groups/${groupId}/settings`,
      updateData
    )
    return data
  }

  async runGroupMonitoring(groupId: number) {
    const { data } = await this.client.post<StatusResponse>(
      `/monitoring/groups/${groupId}/run`
    )
    return data
  }

  async runMonitoringCycle() {
    const { data } = await this.client.post<MonitoringRunResult>(
      '/monitoring/run-cycle'
    )
    return data
  }
}

// Экспортируем единственный экземпляр
export const api = new APIClient()

// Типы для error handling
export class APIClientError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message)
    this.name = 'APIClientError'
  }
}

// Утилиты для работы с API
export const createQueryKey = {
  groups: (params?: any) => ['groups', params] as const,
  group: (id: number) => ['groups', id] as const,
  groupStats: (id: number) => ['groups', id, 'stats'] as const,

  keywords: (params?: any) => ['keywords', params] as const,
  keyword: (id: number) => ['keywords', id] as const,
  keywordCategories: () => ['keywords', 'categories'] as const,

  comments: (params?: any) => ['comments', params] as const,
  comment: (id: number) => ['comments', id] as const,

  parserState: () => ['parser', 'state'] as const,
  parserStats: () => ['parser', 'stats'] as const,
  parserRuns: () => ['parser', 'tasks'] as const,

  globalStats: () => ['stats', 'global'] as const,
  dashboardStats: () => ['stats', 'dashboard'] as const,

  monitoringStats: () => ['monitoring', 'stats'] as const,
  monitoringGroups: (params?: any) => ['monitoring', 'groups', params] as const,
  monitoringGroup: (id: number) => ['monitoring', 'groups', id] as const,
}
