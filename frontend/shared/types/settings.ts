/**
 * Типы и константы для настроек приложения
 */

// Настройки VK API
export interface VKAPISettings {
  access_token: string
  api_version: string
  requests_per_second: number
}

// Настройки мониторинга
export interface MonitoringSettings {
  scheduler_interval_seconds: number
  max_concurrent_groups: number
  group_delay_seconds: number
  auto_start_scheduler: boolean
}

// Настройки базы данных
export interface DatabaseSettings {
  pool_size: number
  max_overflow: number
  pool_recycle: number
}

// Настройки логирования
export interface LoggingSettings {
  level: string
  format: string
  include_timestamp: boolean
}

// Настройки пользовательского интерфейса
export interface UISettings {
  theme: 'light' | 'dark' | 'system'
  auto_refresh: boolean
  refresh_interval: number
  items_per_page: number
  show_notifications: boolean
}

// Полные настройки приложения
export interface ApplicationSettings {
  vk_api: VKAPISettings
  monitoring: MonitoringSettings
  database: DatabaseSettings
  logging: LoggingSettings
  ui: UISettings
}

// Запрос на обновление настроек
export interface SettingsUpdateRequest {
  vk_api?: VKAPISettings
  monitoring?: MonitoringSettings
  database?: DatabaseSettings
  logging?: LoggingSettings
  ui?: UISettings
}

// Ответ с настройками
export interface SettingsResponse {
  settings: ApplicationSettings
  message: string
}

// Статус здоровья настроек
export interface SettingsHealthStatus {
  status: 'healthy' | 'warning' | 'error'
  message: string
  details?: Record<string, any>
  settings_valid?: boolean
  database_connected?: boolean
  redis_connected?: boolean
  vk_api_accessible?: boolean
  last_check?: string
}

// Опции для темы
export const THEME_OPTIONS = [
  { value: 'light', label: 'Светлая' },
  { value: 'dark', label: 'Темная' },
  { value: 'system', label: 'Системная' },
] as const

// Опции уровней логирования
export const LOG_LEVEL_OPTIONS = [
  { value: 'DEBUG', label: 'Debug' },
  { value: 'INFO', label: 'Info' },
  { value: 'WARNING', label: 'Warning' },
  { value: 'ERROR', label: 'Error' },
  { value: 'CRITICAL', label: 'Critical' },
] as const

// Опции формата логов
export const LOG_FORMAT_OPTIONS = [
  { value: 'json', label: 'JSON' },
  { value: 'text', label: 'Текст' },
] as const

// Валидационные правила для настроек
export const SETTINGS_VALIDATION = {
  vk_api: {
    access_token: { required: true, minLength: 10 },
    api_version: { required: true, pattern: /^\d+\.\d+$/ },
    requests_per_second: { required: true, min: 1, max: 20 },
  },
  monitoring: {
    scheduler_interval_seconds: { required: true, min: 60, max: 3600 },
    max_concurrent_groups: { required: true, min: 1, max: 50 },
    group_delay_seconds: { required: true, min: 0, max: 10 },
  },
  database: {
    pool_size: { required: true, min: 5, max: 50 },
    max_overflow: { required: true, min: 10, max: 100 },
    pool_recycle: { required: true, min: 300, max: 7200 },
  },
  logging: {
    level: {
      required: true,
      options: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    },
    format: { required: true, options: ['json', 'text'] },
  },
  ui: {
    theme: {
      required: true,
      options: ['light', 'dark', 'system'],
    },
    refresh_interval: { required: true, min: 10, max: 300 },
    items_per_page: { required: true, min: 10, max: 100 },
  },
} as const
