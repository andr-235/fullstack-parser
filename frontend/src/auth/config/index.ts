/**
 * Экспорт конфигурации системы аутентификации
 */

export { AuthConfigManager, authConfig, useAuthConfig, defaultAuthConfig } from './auth.config'
export type { AuthConfig, AuthConfiguration } from '../types/auth.types'

export {
  AUTH_ERROR_CODES,
  AUTH_ERROR_MESSAGES,
  USER_ROLES,
  USER_PERMISSIONS,
  TOKEN_SETTINGS,
  VALIDATION_RULES,
  PAGINATION_SETTINGS,
  CACHE_SETTINGS,
  API_SETTINGS,
  LOGGING_SETTINGS,
  SECURITY_SETTINGS,
  I18N_SETTINGS,
  FILE_SETTINGS,
  NOTIFICATION_SETTINGS,
  ANIMATION_SETTINGS,
  TESTING_SETTINGS
} from './constants'
