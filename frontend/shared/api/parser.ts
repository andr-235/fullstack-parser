/**
 * API для работы с парсером
 */

import { httpClient } from '@/shared/lib/http-client'
import type {
  ParseRequest,
  ParseResponse,
  ParserState,
  ParserStats,
  ParserGlobalStats,
  ParseTaskListResponse,
  ParserTaskFilters,
  StartBulkParserRequest,
  ParseStatus,
  StopParseRequest,
  StopParseResponse,
} from '@/entities/parser'

export const parserApi = {
  async getParserState(): Promise<ParserState> {
    return httpClient.get('/api/v1/parser/state')
  },

  async getParserStats(): Promise<ParserStats> {
    return httpClient.get('/api/v1/parser/stats')
  },

  async getGlobalStats(): Promise<ParserGlobalStats> {
    return httpClient.get('/api/v1/parser/stats')
  },

  async getTasks(params?: ParserTaskFilters): Promise<ParseTaskListResponse> {
    return httpClient.get('/api/v1/parser/tasks', params)
  },

  async getTaskHistory(params?: ParserTaskFilters): Promise<ParseTaskListResponse> {
    return httpClient.get('/api/v1/parser/history', params)
  },

  async createTask(taskData: ParseRequest): Promise<ParseResponse> {
    return httpClient.post('/api/v1/parser/tasks', taskData)
  },

  async startBulkParse(formData: StartBulkParserRequest): Promise<ParseResponse> {
    return httpClient.post('/api/v1/parser/bulk-start', formData)
  },

  async getParseStatus(taskId: string): Promise<ParseStatus> {
    return httpClient.get(`/api/v1/parser/tasks/${taskId}/status`)
  },

  async stopParse(taskId: string, data: StopParseRequest): Promise<StopParseResponse> {
    return httpClient.post(`/api/v1/parser/tasks/${taskId}/stop`, data)
  },

  async deleteTask(taskId: string): Promise<void> {
    return httpClient.delete(`/api/v1/parser/tasks/${taskId}`)
  },
}
