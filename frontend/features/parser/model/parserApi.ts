import { apiClient } from '@/shared/api/client';
import type {
  ParseRequest,
  ParseResponse,
  ParseStatus,
  ParseTaskListResponse,
  ParserStats,
  ParserState,
  StopParseRequest,
  StopParseResponse,
} from '@/entities/parser/types';

// API endpoints
const PARSER_ENDPOINTS = {
  parse: '/parser/parse',
  status: (taskId: string) => `/parser/status/${taskId}`,
  tasks: '/parser/tasks',
  stop: '/parser/stop',
  stats: '/parser/stats',
  state: '/parser/state',
} as const;

/**
 * API клиент для работы с парсером
 */
export const parserApi = {
  /**
   * Запустить парсинг групп
   */
  async startParsing(request: ParseRequest): Promise<ParseResponse> {
    const response = await apiClient.post<ParseResponse>(
      PARSER_ENDPOINTS.parse,
      request
    );
    return response.data;
  },

  /**
   * Получить статус задачи
   */
  async getTaskStatus(taskId: string): Promise<ParseStatus> {
    const response = await apiClient.get<ParseStatus>(
      PARSER_ENDPOINTS.status(taskId)
    );
    return response.data;
  },

  /**
   * Получить список всех задач
   */
  async getTasks(): Promise<ParseTaskListResponse> {
    const response = await apiClient.get<ParseTaskListResponse>(
      PARSER_ENDPOINTS.tasks
    );
    return response.data;
  },

  /**
   * Остановить парсинг
   */
  async stopParsing(request: StopParseRequest): Promise<StopParseResponse> {
    const response = await apiClient.post<StopParseResponse>(
      PARSER_ENDPOINTS.stop,
      request
    );
    return response.data;
  },

  /**
   * Получить статистику парсера
   */
  async getStats(): Promise<ParserStats> {
    const response = await apiClient.get<ParserStats>(
      PARSER_ENDPOINTS.stats
    );
    return response.data;
  },

  /**
   * Получить состояние парсера
   */
  async getState(): Promise<ParserState> {
    const response = await apiClient.get<ParserState>(
      PARSER_ENDPOINTS.state
    );
    return response.data;
  },
};