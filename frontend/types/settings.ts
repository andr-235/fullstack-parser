/**
 * Типы для настроек приложения
 */

export interface VKAPISettings {
  access_token: string
  api_version: string
  requests_per_second: number
}

export interface MonitoringSettings {
  scheduler_interval_seconds: number
  max_concurrent_groups: number
  group_delay_seconds: number
  auto_start_scheduler: boolean
}

export interface DatabaseSettings {
  pool_size: number
  max_overflow: number
  pool_recycle: number
}

export interface LoggingSettings {
  level: string
  format: string
  include_timestamp: boolean
}

export interface UISettings {
  theme: 'light' | 'dark' | 'system'
  auto_refresh: boolean
  refresh_interval: number
  items_per_page: number
  show_notifications: boolean
}

export interface ApplicationSettings {
  vk_api: VKAPISettings
  monitoring: MonitoringSettings
  database: DatabaseSettings
  logging: LoggingSettings
  ui: UISettings
}

export interface SettingsUpdateRequest {
  vk_api?: Partial<VKAPISettings>
  monitoring?: Partial<MonitoringSettings>
  database?: Partial<DatabaseSettings>
  logging?: Partial<LoggingSettings>
  ui?: Partial<UISettings>
}

export interface SettingsResponse {
  settings: ApplicationSettings
  message: string
}

export interface SettingsHealthStatus {
  status: 'healthy' | 'unhealthy'
  settings_valid: boolean
  database_connected: boolean
  redis_connected: boolean
  vk_api_accessible: boolean
  last_check?: string
  error?: string
}

/**
 * Дефолтные настройки
 */
export const DEFAULT_SETTINGS: ApplicationSettings = {
  vk_api: {
    access_token: '',
    api_version: '5.131',
    requests_per_second: 3,
  },
  monitoring: {
    scheduler_interval_seconds: 300,
    max_concurrent_groups: 10,
    group_delay_seconds: 1,
    auto_start_scheduler: false,
  },
  database: {
    pool_size: 10,
    max_overflow: 20,
    pool_recycle: 3600,
  },
  logging: {
    level: 'INFO',
    format: 'json',
    include_timestamp: true,
  },
  ui: {
    theme: 'system',
    auto_refresh: true,
    refresh_interval: 30,
    items_per_page: 20,
    show_notifications: true,
  },
}

/**
 * Валидация настроек
 */
export const SETTINGS_VALIDATION = {
  vk_api: {
    requests_per_second: { min: 1, max: 20 },
  },
  monitoring: {
    scheduler_interval_seconds: { min: 60, max: 3600 },
    max_concurrent_groups: { min: 1, max: 50 },
    group_delay_seconds: { min: 0, max: 10 },
  },
  database: {
    pool_size: { min: 5, max: 50 },
    max_overflow: { min: 10, max: 100 },
    pool_recycle: { min: 300, max: 7200 },
  },
  ui: {
    refresh_interval: { min: 10, max: 300 },
    items_per_page: { min: 10, max: 100 },
  },
} as const

/**
 * Опции для селектов
 */
export const LOG_LEVEL_OPTIONS = [
  { value: 'DEBUG', label: 'Debug' },
  { value: 'INFO', label: 'Info' },
  { value: 'WARNING', label: 'Warning' },
  { value: 'ERROR', label: 'Error' },
  { value: 'CRITICAL', label: 'Critical' },
] as const

export const THEME_OPTIONS = [
  { value: 'light', label: 'Светлая' },
  { value: 'dark', label: 'Темная' },
  { value: 'system', label: 'Системная' },
] as const

export const LOG_FORMAT_OPTIONS = [
  { value: 'json', label: 'JSON' },
  { value: 'text', label: 'Текст' },
] as const
