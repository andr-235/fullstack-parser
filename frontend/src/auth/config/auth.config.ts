/**
 * Конфигурация системы аутентификации
 * Все настройки загружаются из переменных окружения
 */

import type { AuthConfig, AuthConfiguration } from '../types/auth.types'


/**
 * Класс конфигурации аутентификации
 */
export class AuthConfigManager {
  private static instance: AuthConfigManager
  private config: AuthConfiguration

  private constructor() {
    this.config = this.loadConfiguration()
  }

  /**
   * Получение экземпляра синглтона
   */
  public static getInstance(): AuthConfigManager {
    if (!AuthConfigManager.instance) {
      AuthConfigManager.instance = new AuthConfigManager()
    }
    return AuthConfigManager.instance
  }

  /**
   * Загрузка конфигурации из переменных окружения
   */
  private loadConfiguration(): AuthConfiguration {
    const apiTimeout = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000', 10);
    const tokenRefreshThreshold = parseInt(import.meta.env.VITE_AUTH_TOKEN_REFRESH_THRESHOLD || '300000', 10);
    const cacheTtl = parseInt(import.meta.env.VITE_CACHE_TTL || '3600000', 10);
    const maxFileSize = parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '5242880', 10);
    const defaultPageSize = parseInt(import.meta.env.VITE_DEFAULT_PAGE_SIZE || '20', 10);
    const maxPageSize = parseInt(import.meta.env.VITE_MAX_PAGE_SIZE || '100', 10);

    return {
      // API настройки
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      apiTimeout: isNaN(apiTimeout) ? 10000 : apiTimeout,

      // Настройки токенов
      tokenRefreshThreshold: isNaN(tokenRefreshThreshold) ? 300000 : tokenRefreshThreshold,
      autoRefresh: import.meta.env.VITE_AUTH_AUTO_REFRESH !== 'false',

      // Редиректы
      redirectAfterLogin: import.meta.env.VITE_AUTH_REDIRECT_AFTER_LOGIN || '/',
      redirectAfterLogout: import.meta.env.VITE_AUTH_REDIRECT_AFTER_LOGOUT || '/auth/login',

      // Функциональность
      enableRegistration: import.meta.env.VITE_ENABLE_REGISTRATION !== 'false',
      enablePasswordReset: import.meta.env.VITE_ENABLE_PASSWORD_RESET !== 'false',
      enableSocialLogin: import.meta.env.VITE_ENABLE_SOCIAL_LOGIN === 'true',
      enableTwoFactorAuth: import.meta.env.VITE_ENABLE_TWO_FACTOR_AUTH === 'true',

      // Безопасность
      enableHttps: import.meta.env.VITE_ENABLE_HTTPS === 'true',
      corsEnabled: import.meta.env.VITE_CORS_ENABLED !== 'false',

      // Логирование
      logLevel: (import.meta.env.VITE_LOG_LEVEL as AuthConfiguration['logLevel']) || 'info',

      // Кеширование
      cacheTtl: isNaN(cacheTtl) ? 3600000 : cacheTtl,

      // Интернационализация
      defaultLanguage: import.meta.env.VITE_DEFAULT_LANGUAGE || 'ru',
      supportedLanguages: (import.meta.env.VITE_SUPPORTED_LANGUAGES || 'ru,en').split(','),

      // Социальные сети
      googleClientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
      facebookAppId: import.meta.env.VITE_FACEBOOK_APP_ID || '',
      githubClientId: import.meta.env.VITE_GITHUB_CLIENT_ID || '',

      // Мониторинг
      sentryDsn: import.meta.env.VITE_SENTRY_DSN || '',
      googleAnalyticsId: import.meta.env.VITE_GOOGLE_ANALYTICS_ID || '',

      // Файлы
      maxFileSize: isNaN(maxFileSize) ? 5242880 : maxFileSize,
      allowedFileTypes: (import.meta.env.VITE_ALLOWED_FILE_TYPES || 'image/jpeg,image/png,image/gif,application/pdf').split(','),

      // Пагинация
      defaultPageSize: isNaN(defaultPageSize) ? 20 : defaultPageSize,
      maxPageSize: isNaN(maxPageSize) ? 100 : maxPageSize,

      // Service Worker
      enableServiceWorker: import.meta.env.VITE_ENABLE_SERVICE_WORKER === 'true',

      // Разработка
      enableHotReload: import.meta.env.VITE_ENABLE_HOT_RELOAD !== 'false',
      enableErrorBoundary: import.meta.env.VITE_ENABLE_ERROR_BOUNDARY !== 'false',
      enablePerformanceMonitoring: import.meta.env.VITE_ENABLE_PERFORMANCE_MONITORING === 'true',
      enableDevtools: import.meta.env.VITE_ENABLE_DEVTOOLS !== 'false'
    }
  }

  /**
   * Получение конфигурации
   */
  public getConfig(): AuthConfiguration {
    return { ...this.config }
  }

  /**
   * Получение конкретного параметра конфигурации
   */
  public get<K extends keyof AuthConfiguration>(key: K): AuthConfiguration[K] {
    return this.config[key as K]
  }

  /**
   * Проверка доступности функциональности
   */
  public isFeatureEnabled(feature: keyof Pick<AuthConfiguration,
    | 'enableRegistration'
    | 'enablePasswordReset'
    | 'enableSocialLogin'
    | 'enableTwoFactorAuth'
  >): boolean {
    return this.config[feature]
  }

  /**
   * Проверка режима разработки
   */
  public isDevelopment(): boolean {
    return import.meta.env.DEV
  }

  /**
   * Проверка продакшн режима
   */
  public isProduction(): boolean {
    return import.meta.env.PROD
  }

  /**
   * Получение API URL для конкретного эндпоинта
   */
  public getApiUrl(endpoint: string): string {
    const baseUrl = this.config.apiBaseUrl!
    return `${baseUrl.replace(/\/$/, '')}/${endpoint.replace(/^\//, '')}`
  }

  /**
   * Получение заголовков для API запросов
   */
  public getApiHeaders(additionalHeaders?: Record<string, string>): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (this.config.corsEnabled) {
      headers['X-Requested-With'] = 'XMLHttpRequest'
    }

    if (additionalHeaders) {
      Object.assign(headers, additionalHeaders)
    }

    return headers
  }

  /**
   * Получение настроек для axios
   */
  public getAxiosConfig(): any {
    return {
      baseURL: this.config.apiBaseUrl!,
      timeout: this.config.apiTimeout,
      headers: this.getApiHeaders(),
    }
  }

  /**
   * Валидация конфигурации
   */
  public validateConfig(): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!this.config.apiBaseUrl) {
      errors.push('API base URL не настроен')
    }

    if (isNaN(this.config.apiTimeout) || this.config.apiTimeout <= 0) {
      errors.push('API timeout должен быть положительным числом')
    }

    if (isNaN(this.config.tokenRefreshThreshold) || this.config.tokenRefreshThreshold <= 0) {
      errors.push('Token refresh threshold должен быть положительным числом')
    }

    if (isNaN(this.config.maxFileSize) || this.config.maxFileSize <= 0) {
      errors.push('Max file size должен быть положительным числом')
    }

    if (isNaN(this.config.defaultPageSize) || this.config.defaultPageSize <= 0) {
      errors.push('Default page size должен быть положительным числом')
    }

    if (isNaN(this.config.maxPageSize) || this.config.maxPageSize < this.config.defaultPageSize) {
      errors.push('Max page size не может быть меньше default page size')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * Перезагрузка конфигурации
   */
  public reloadConfig(): void {
    this.config = this.loadConfiguration()
  }
}

/**
 * Экземпляр конфигурации для использования в приложении
 */
export const authConfig = AuthConfigManager.getInstance()

/**
 * Хелперы для быстрого доступа к конфигурации
 */
export const useAuthConfig = () => authConfig

/**
 * Дефолтная конфигурация для TypeScript
 */
export const defaultAuthConfig: AuthConfiguration = {
  apiBaseUrl: 'http://localhost:8000/api',
  apiTimeout: 10000,
  tokenRefreshThreshold: 300000,
  autoRefresh: true,
  redirectAfterLogin: '/',
  redirectAfterLogout: '/auth/login',
  enableRegistration: true,
  enablePasswordReset: true,
  enableSocialLogin: false,
  enableTwoFactorAuth: false,
  enableHttps: false,
  corsEnabled: true,
  logLevel: 'info',
  cacheTtl: 3600000,
  defaultLanguage: 'ru',
  supportedLanguages: ['ru', 'en'],
  googleClientId: '',
  facebookAppId: '',
  githubClientId: '',
  sentryDsn: '',
  googleAnalyticsId: '',
  maxFileSize: 5242880,
  allowedFileTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'],
  defaultPageSize: 20,
  maxPageSize: 100,
  enableServiceWorker: false,
  enableHotReload: true,
  enableErrorBoundary: true,
  enablePerformanceMonitoring: false,
  enableDevtools: true
}