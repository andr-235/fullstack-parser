import { apiClient } from '@/shared/api/client';
import type {
  ParseRequest,
  ParseResponse,
  ParseStatus,
  ParseTaskListResponse,
  StopParseResponse,
  ParserStats,
  ParserState,
  TaskFilters,
} from '../types';

/**
 * API клиент для работы с парсером VK данных
 */
export const parserApi = {
  /**
   * Запустить парсинг групп VK
   */
  async startParsing(request: ParseRequest): Promise<ParseResponse> {
    const response = await apiClient.post<ParseResponse>('/parser/parse', request);
    return response.data;
  },

  /**
   * Получить статус задачи парсинга
   */
  async getTaskStatus(taskId: string): Promise<ParseStatus> {
    const response = await apiClient.get<ParseStatus>(`/parser/status/${taskId}`);
    return response.data;
  },

  /**
   * Получить список всех задач парсинга
   */
  async getTasks(filters: TaskFilters = {}): Promise<ParseTaskListResponse> {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (Array.isArray(value)) {
          value.forEach(v => params.append(key, v));
        } else {
          params.append(key, value.toString());
        }
      }
    });

    const queryString = params.toString();
    const url = queryString ? `/parser/tasks?${queryString}` : '/parser/tasks';

    const response = await apiClient.get<ParseTaskListResponse>(url);
    return response.data;
  },

  /**
   * Остановить парсинг
   */
  async stopParsing(request: { task_id?: string } = {}): Promise<StopParseResponse> {
    const response = await apiClient.post<StopParseResponse>('/parser/stop', request);
    return response.data;
  },

  /**
   * Получить статистику парсера
   */
  async getStats(): Promise<ParserStats> {
    const response = await apiClient.get<ParserStats>('/parser/stats');
    return response.data;
  },

  /**
   * Получить состояние парсера
   */
  async getState(): Promise<ParserState> {
    const response = await apiClient.get<ParserState>('/parser/state');
    return response.data;
  },

  /**
   * Проверить доступность API парсера
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get<{ status: string; timestamp: string }>('/parser/health');
    return response.data;
  },
};