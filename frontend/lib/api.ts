import axios, { AxiosInstance, AxiosError } from 'axios'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  VKGroupStats,
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
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
} from '@/types/api'

/**
 * Конфигурация API клиента
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
}
