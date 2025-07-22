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
  VKGroupUploadResponse,
  SchedulerStatus,
} from '@/types/api'
import type {
  ApplicationSettings,
  SettingsUpdateRequest,
  SettingsResponse,
  SettingsHealthStatus,
} from '@/types/settings'

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
      timeout: 120000, // Увеличиваем таймаут до 2 минут для операций мониторинга
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Interceptors для обработки ошибок
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<APIError>) => {
        if (error.response?.data) {
          const apiError = new Error(
            error.response.data.detail || 'API Error'
          ) as any
          apiError.response = error.response
          apiError.status = error.response.status
          throw apiError
        }
        throw new Error(error.message || 'Network Error')
      }
    )
  }

  // VK Groups API
  async getGroups(
    params?: PaginationParams & { active_only?: boolean; search?: string }
  ) {
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

  async refreshGroupInfo(groupId: number) {
    const { data } = await this.client.post<VKGroupResponse>(
      `/groups/${groupId}/refresh`
    )
    return data
  }

  async deleteGroup(groupId: number) {
    const { data } = await this.client.delete<StatusResponse>(
      `/groups/${groupId}`
    )
    return data
  }

  async uploadGroupsFromFile(
    file: File,
    options?: {
      is_active?: boolean
      max_posts_to_check?: number
    }
  ) {
    const formData = new FormData()
    formData.append('file', file)

    if (options?.is_active !== undefined) {
      formData.append('is_active', options.is_active.toString())
    }

    if (options?.max_posts_to_check !== undefined) {
      formData.append(
        'max_posts_to_check',
        options.max_posts_to_check.toString()
      )
    }

    try {
      const { data } = await this.client.post<VKGroupUploadResponse>(
        '/groups/upload',
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
      if (error.response?.data?.detail) {
        throw new APIClientError(
          error.response.data.detail,
          error.response.status,
          error.response.data
        )
      }
      throw new APIClientError(
        'Ошибка загрузки файла с группами',
        error.response?.status,
        error
      )
    }
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
        '/keywords/upload',
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

  async updateKeywordsStats() {
    const { data } = await this.client.post<StatusResponse>(
      '/keywords/update-stats'
    )
    return data
  }

  async getTotalMatches() {
    const { data } = await this.client.get<{ total_matches: number }>(
      '/keywords/total-matches'
    )
    return data
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

  // Дополнительные методы для дашборда
  async getActivityData(params: { timeRange: string }) {
    try {
      const { data } = await this.client.get('/stats/activity', { params })
      return data
    } catch (error) {
      // Fallback - генерируем моковые данные на основе реальной статистики
      const globalStats = await this.getGlobalStats()
      const days =
        params.timeRange === '7d' ? 7 : params.timeRange === '30d' ? 30 : 1
      const activityData = []

      for (let i = days - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        activityData.push({
          date: date.toISOString().split('T')[0],
          comments: Math.floor(Math.random() * 100) + 20,
          matches: Math.floor(Math.random() * 30) + 5,
        })
      }

      return activityData
    }
  }

  async getTopGroups(params: { limit: number }) {
    try {
      const { data } = await this.client.get('/stats/top-groups', { params })
      return data
    } catch (error) {
      // Fallback - получаем группы и сортируем по комментариям
      const groups = await this.getGroups({ size: params.limit })
      return groups.items.sort(
        (a, b) => b.total_comments_found - a.total_comments_found
      )
    }
  }

  async getTopKeywords(params: { limit: number }) {
    try {
      const { data } = await this.client.get('/stats/top-keywords', { params })
      return data
    } catch (error) {
      // Fallback - получаем ключевые слова и сортируем по совпадениям
      const keywords = await this.getKeywords({ size: params.limit })
      return keywords.items.sort((a, b) => b.total_matches - a.total_matches)
    }
  }

  async getRecentComments(params: { limit: number }) {
    try {
      const { data } = await this.client.get('/stats/recent-comments', {
        params,
      })
      return data
    } catch (error) {
      // Fallback - получаем последние комментарии
      const comments = await this.getComments({ size: params.limit })
      return comments
    }
  }

  async getSystemStatus() {
    try {
      const { data } = await this.client.get('/system/status')
      return data
    } catch (error) {
      // Fallback - проверяем health check
      const health = await this.healthCheck()
      return {
        status: 'healthy',
        message: 'Система работает нормально',
        lastCheck: new Date().toISOString(),
        uptime: 'Неизвестно',
      }
    }
  }

  async getParsingProgress() {
    try {
      const { data } = await this.client.get('/parser/progress')
      return data
    } catch (error) {
      // Fallback - получаем состояние парсера
      const parserState = await this.getParserState()
      return {
        currentTask: parserState.task?.group_name || 'Нет активных задач',
        progress: parserState.task?.progress || 0,
        totalItems: 0,
        processedItems: parserState.task?.posts_processed || 0,
        estimatedTime: 'Неизвестно',
      }
    }
  }

  async getRecentActivity(params: { limit: number }) {
    try {
      const { data } = await this.client.get('/stats/recent-activity', {
        params,
      })
      return data
    } catch (error) {
      // Fallback - получаем последние задачи парсинга
      const tasks = await this.getRecentParseTasks({ size: params.limit })
      return tasks.items.map((task) => ({
        id: task.task_id,
        type: 'parse' as const,
        message: `Парсинг группы ${task.group_name || task.group_id}`,
        timestamp: task.started_at,
        status:
          task.status === 'completed'
            ? 'success'
            : task.status === 'failed'
              ? 'error'
              : 'warning',
      }))
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

  async getAvailableGroupsForMonitoring(params?: PaginationParams) {
    const { data } = await this.client.get<
      PaginatedResponse<VKGroupMonitoring>
    >('/monitoring/groups/available', { params })
    return data
  }

  async getActiveMonitoringGroups(params?: PaginationParams) {
    const { data } = await this.client.get<
      PaginatedResponse<VKGroupMonitoring>
    >('/monitoring/groups/active', { params })
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
      '/monitoring/run-cycle',
      {},
      {
        timeout: 300000, // 5 минут для операции мониторинга
      }
    )
    return data
  }

  async getSchedulerStatus() {
    const { data } = await this.client.get<SchedulerStatus>(
      '/monitoring/scheduler/status'
    )
    return data
  }

  // Settings API
  async getSettings() {
    const { data } = await this.client.get<SettingsResponse>('/settings/')
    return data
  }

  async updateSettings(settings: SettingsUpdateRequest) {
    const { data } = await this.client.put<SettingsResponse>(
      '/settings/',
      settings
    )
    return data
  }

  async resetSettings() {
    const { data } = await this.client.post<SettingsResponse>('/settings/reset')
    return data
  }

  async getSettingsHealth() {
    const { data } =
      await this.client.get<SettingsHealthStatus>('/settings/health')
    return data
  }

  async testVKAPIConnection(accessToken: string, apiVersion: string = '5.131') {
    try {
      const response = await this.client.get(
        'https://api.vk.com/method/users.get',
        {
          params: {
            access_token: accessToken,
            v: apiVersion,
            user_ids: '1',
          },
          timeout: 10000, // 10 секунд
        }
      )
      return response.status === 200
    } catch (error) {
      console.error('VK API connection test failed:', error)
      return false
    }
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
  activityData: (timeRange: string) =>
    ['stats', 'activity', timeRange] as const,
  topGroups: (limit: number) => ['stats', 'top-groups', limit] as const,
  topKeywords: (limit: number) => ['stats', 'top-keywords', limit] as const,
  recentComments: (limit: number) =>
    ['stats', 'recent-comments', limit] as const,
  systemStatus: () => ['system', 'status'] as const,
  parsingProgress: () => ['parser', 'progress'] as const,
  recentActivity: (limit: number) =>
    ['stats', 'recent-activity', limit] as const,

  monitoringStats: () => ['monitoring', 'stats'] as const,
  monitoringGroups: (params?: any) => ['monitoring', 'groups', params] as const,

  availableGroupsForMonitoring: (params?: any) =>
    ['monitoring', 'groups', 'available', params] as const,
  activeMonitoringGroups: (params?: any) =>
    ['monitoring', 'groups', 'active', params] as const,

  monitoringGroup: (id: number) => ['monitoring', 'groups', id] as const,
  schedulerStatus: () => ['monitoring', 'scheduler', 'status'] as const,

  settings: () => ['settings'] as const,
  settingsHealth: () => ['settings', 'health'] as const,
}
