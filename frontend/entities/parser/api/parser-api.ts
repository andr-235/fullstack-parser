import { httpClient } from '@/shared/lib'
import { getRoutePath, PARSER_ROUTES } from '@/shared/config/routes'

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
  ParseTask,
} from '../types'

// API для запуска парсинга
export const startParser = async (taskData: ParseTaskCreate): Promise<ParseTaskResponse> => {
  return httpClient.post(getRoutePath(PARSER_ROUTES.PARSE), taskData)
}

// API для массового запуска парсинга
export const startBulkParser = async (bulkData: StartBulkParserForm): Promise<BulkParseResponse> => {
  return httpClient.post(getRoutePath(PARSER_ROUTES.BULK_START), bulkData)
}

// API для остановки парсинга
export const stopParser = async (request: StopParseRequest = {}): Promise<StopParseResponse> => {
  return httpClient.post(getRoutePath(PARSER_ROUTES.STOP), request)
}

// API для получения состояния парсера
export const getParserState = async (): Promise<ParserState> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.STATE))
}

// API для получения статистики парсера
export const getParserStats = async (): Promise<ParserStats> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.STATS))
}

// API для получения глобальной статистики парсера
export const getParserGlobalStats = async (): Promise<ParserGlobalStats> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.GLOBAL_STATS))
}

// API для получения списка задач
export const getParserTasks = async (filters?: ParserTaskFilters): Promise<ParserTasksResponse> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.TASKS), { params: filters })
}

// API для получения конкретной задачи
export const getParserTask = async (taskId: string): Promise<ParseStatus> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.TASK_STATUS(taskId)))
}

// API для получения истории парсера
export const getParserHistory = async (page = 1, size = 10): Promise<ParserHistoryResponse> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.HISTORY), { params: { page, size } })
}

// API для получения статуса задачи
export const getTaskStatus = async (taskId: string): Promise<ParseStatus> => {
  return httpClient.get(getRoutePath(PARSER_ROUTES.TASK_STATUS(taskId)))
}
