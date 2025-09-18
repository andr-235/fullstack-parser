/**
 * Типы данных для модуля Parser
 *
 * Определяет интерфейсы и типы для работы с парсингом VK данных
 */

// Статусы задач парсинга
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'stopped';

// Приоритеты задач
export type TaskPriority = 'low' | 'normal' | 'high';

// Информация о группе VK
export interface VKGroupInfo {
  id: number;
  name: string;
  screen_name: string;
  description?: string;
  members_count?: number;
  is_closed?: boolean;
  photo_200?: string;
}

// Информация о посте VK
export interface VKPostInfo {
  id: number;
  text: string;
  date: string;
  likes: number;
  reposts: number;
  comments: number;
  attachments?: any[];
}

// Информация о комментарии VK
export interface VKCommentInfo {
  id: number;
  text: string;
  date: string;
  likes: number;
  from_id: number;
  thread?: {
    count: number;
    items?: VKCommentInfo[];
  };
}

// Результат парсинга группы
export interface ParseResult {
  group_id: number;
  group_info?: VKGroupInfo;
  posts_found: number;
  comments_found: number;
  posts_saved: number;
  comments_saved: number;
  errors: string[];
  duration_seconds: number;
  success: boolean;
}

// Задача парсинга
export interface ParsingTask {
  task_id: string;
  group_ids: number[];
  config: ParseConfig;
  status: TaskStatus;
  priority: TaskPriority;
  progress: number;
  current_group?: number;
  groups_completed: number;
  groups_total: number;
  posts_found: number;
  comments_found: number;
  errors: string[];
  result?: any;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  duration?: number;
}

// Конфигурация парсинга
export interface ParseConfig {
  max_posts: number;
  max_comments_per_post: number;
  force_reparse: boolean;
}

// Запрос на парсинг
export interface ParseRequest {
  group_ids: number[];
  max_posts?: number;
  max_comments_per_post?: number;
  force_reparse?: boolean;
  priority?: TaskPriority;
}

// Запрос на запуск парсера
export interface StartParserRequest extends ParseRequest {
  // Наследует все поля от ParseRequest
}

// Запрос на запуск массового парсера
export interface StartBulkParserRequest extends ParseRequest {
  // Наследует все поля от ParseRequest
}

// Ответ на запрос парсинга
export interface ParseResponse {
  task_id: string;
  status: TaskStatus;
  group_ids: number[];
  created_at: string;
  priority: TaskPriority;
}

// Статус задачи парсинга
export interface ParseStatus {
  task_id: string;
  status: TaskStatus;
  progress: number;
  current_group?: number;
  groups_completed: number;
  groups_total: number;
  posts_found: number;
  comments_found: number;
  errors: string[];
  started_at?: string;
  completed_at?: string;
  duration?: number;
  priority: TaskPriority;
}

// Статистика парсера
export interface ParserStats {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  running_tasks: number;
  success_rate: number;
}

// Состояние парсера
export interface ParserState {
  is_running: boolean;
  active_tasks: number;
  total_tasks_processed: number;
  total_posts_found: number;
  total_comments_found: number;
  last_activity?: string;
}

// Глобальная статистика парсера
export interface ParserGlobalStats {
  total_posts_found: number;
  total_comments_found: number;
  completed_tasks: number;
  failed_tasks: number;
  average_task_duration: number;
  last_activity: string;
  is_running: boolean;
}

// Запрос на остановку парсинга
export interface StopParseRequest {
  task_id?: string;
}

// Ответ на остановку парсинга
export interface StopParseResponse {
  stopped_tasks: string[];
  message: string;
}

// Список задач парсинга
export interface ParseTaskListResponse {
  tasks: ParsingTask[];
  total: number;
}

// Ошибка VK API
export interface VKAPIError {
  error_code: number;
  error_message: string;
  request_params?: any[];
}

// Фильтры для списка задач
export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  limit?: number;
  offset?: number;
  sort_by?: 'created_at' | 'started_at' | 'completed_at';
  sort_order?: 'asc' | 'desc';
}

// Состояние UI компонентов
export interface ParserUIState {
  isLoading: boolean;
  error?: string;
  data?: any;
}

// Типы для форм
export interface ParserFormData {
  group_ids: string;
  max_posts: number;
  max_comments_per_post: number;
  force_reparse: boolean;
  priority: TaskPriority;
}

// Валидационные ошибки форм
export interface ParserFormErrors {
  group_ids?: string;
  max_posts?: string;
  max_comments_per_post?: string;
  priority?: string;
}

// Экспорт всех типов
export type {
  TaskStatus as ParserTaskStatus,
  TaskPriority as ParserTaskPriority,
  ParserGlobalStats as ParserParserGlobalStats,
  VKGroupInfo as ParserVKGroupInfo,
  VKPostInfo as ParserVKPostInfo,
  VKCommentInfo as ParserVKCommentInfo,
  ParseResult as ParserParseResult,
  ParsingTask as ParserTask,
  ParseConfig as ParserParseConfig,
  ParseRequest as ParserParseRequest,
  ParseResponse as ParserParseResponse,
  ParseResponse as ParserResponse,  // Добавлен алиас для совместимости
  ParseStatus as ParserParseStatus,
  ParserStats as ParserParserStats,
  ParserState as ParserParserState,
  StopParseRequest as ParserStopParseRequest,
  StopParseResponse as ParserStopParseResponse,
  ParseTaskListResponse as ParserParseTaskListResponse,
  VKAPIError as ParserVKAPIError,
  TaskFilters as ParserTaskFilters,
  ParserUIState as ParserParserUIState,
  ParserFormData as ParserParserFormData,
  ParserFormErrors as ParserParserFormErrors,
};