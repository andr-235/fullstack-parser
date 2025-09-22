/**
 * Константы системы аутентификации
 */

// Тип для кодов ошибок
type AuthErrorType = string

/**
 * Коды ошибок аутентификации
 */
export const AUTH_ERROR_CODES = {
  // Ошибки валидации
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  WEAK_PASSWORD: 'WEAK_PASSWORD',
  PASSWORD_MISMATCH: 'PASSWORD_MISMATCH',

  // Ошибки токенов
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_INVALID: 'TOKEN_INVALID',
  TOKEN_MISSING: 'TOKEN_MISSING',
  TOKEN_REFRESH_FAILED: 'TOKEN_REFRESH_FAILED',

  // Ошибки авторизации
  ACCESS_DENIED: 'ACCESS_DENIED',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',
  ACCOUNT_DISABLED: 'ACCOUNT_DISABLED',
  ACCOUNT_LOCKED: 'ACCOUNT_LOCKED',

  // Ошибки сети
  NETWORK_ERROR: 'NETWORK_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',

  // Ошибки системы
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
  CONFIGURATION_ERROR: 'CONFIGURATION_ERROR',
  INITIALIZATION_ERROR: 'INITIALIZATION_ERROR'
} as const

/**
 * Сообщения об ошибках для пользователя
 */
export const AUTH_ERROR_MESSAGES: Record<string, string> = {
  [AUTH_ERROR_CODES.VALIDATION_ERROR]: 'Пожалуйста, проверьте правильность введенных данных',
  [AUTH_ERROR_CODES.INVALID_CREDENTIALS]: 'Неверный email или пароль',
  [AUTH_ERROR_CODES.WEAK_PASSWORD]: 'Пароль слишком слабый. Используйте минимум 8 символов, включая буквы и цифры',
  [AUTH_ERROR_CODES.PASSWORD_MISMATCH]: 'Пароли не совпадают',

  [AUTH_ERROR_CODES.TOKEN_EXPIRED]: 'Сессия истекла. Пожалуйста, войдите снова',
  [AUTH_ERROR_CODES.TOKEN_INVALID]: 'Недействительный токен авторизации',
  [AUTH_ERROR_CODES.TOKEN_MISSING]: 'Токен авторизации отсутствует',
  [AUTH_ERROR_CODES.TOKEN_REFRESH_FAILED]: 'Не удалось обновить токен. Пожалуйста, войдите снова',

  [AUTH_ERROR_CODES.ACCESS_DENIED]: 'Доступ запрещен',
  [AUTH_ERROR_CODES.INSUFFICIENT_PERMISSIONS]: 'Недостаточно прав для выполнения этого действия',
  [AUTH_ERROR_CODES.ACCOUNT_DISABLED]: 'Аккаунт отключен. Обратитесь к администратору',
  [AUTH_ERROR_CODES.ACCOUNT_LOCKED]: 'Аккаунт заблокирован из-за подозрительной активности',

  [AUTH_ERROR_CODES.NETWORK_ERROR]: 'Ошибка сети. Проверьте подключение к интернету',
  [AUTH_ERROR_CODES.SERVER_ERROR]: 'Ошибка сервера. Попробуйте позже',
  [AUTH_ERROR_CODES.TIMEOUT_ERROR]: 'Превышено время ожидания. Попробуйте еще раз',

  [AUTH_ERROR_CODES.UNKNOWN_ERROR]: 'Произошла неизвестная ошибка. Попробуйте еще раз',
  [AUTH_ERROR_CODES.CONFIGURATION_ERROR]: 'Ошибка конфигурации системы',
  [AUTH_ERROR_CODES.INITIALIZATION_ERROR]: 'Ошибка инициализации системы аутентификации'
}

/**
 * Роли пользователей
 */
export const USER_ROLES = {
  ADMIN: 'admin',
  MODERATOR: 'moderator',
  PREMIUM: 'premium',
  USER: 'user'
} as const

/**
 * Разрешения пользователей
 */
export const USER_PERMISSIONS = {
  // Административные разрешения
  MANAGE_USERS: 'manage_users',
  MANAGE_ROLES: 'manage_roles',
  MANAGE_SETTINGS: 'manage_settings',
  VIEW_ANALYTICS: 'view_analytics',
  MANAGE_CONTENT: 'manage_content',

  // Пользовательские разрешения
  EDIT_PROFILE: 'edit_profile',
  DELETE_ACCOUNT: 'delete_account',
  UPLOAD_FILES: 'upload_files',
  DOWNLOAD_FILES: 'download_files',

  // Контент разрешения
  CREATE_POSTS: 'create_posts',
  EDIT_POSTS: 'edit_posts',
  DELETE_POSTS: 'delete_posts',
  PUBLISH_POSTS: 'publish_posts',

  // Комментарии
  CREATE_COMMENTS: 'create_comments',
  EDIT_COMMENTS: 'edit_comments',
  DELETE_COMMENTS: 'delete_comments',
  MODERATE_COMMENTS: 'moderate_comments'
} as const

/**
 * Настройки токенов
 */
export const TOKEN_SETTINGS = {
  // Время жизни токенов (в секундах)
  ACCESS_TOKEN_LIFETIME: 900, // 15 минут
  REFRESH_TOKEN_LIFETIME: 604800, // 7 дней

  // Порог обновления токена (в миллисекундах)
  REFRESH_THRESHOLD: 300000, // 5 минут

  // Максимальное количество попыток обновления
  MAX_REFRESH_ATTEMPTS: 3,

  // Задержка между попытками обновления (в миллисекундах)
  REFRESH_RETRY_DELAY: 1000
} as const

/**
 * Настройки валидации форм
 */
export const VALIDATION_RULES = {
  // Email
  EMAIL_MIN_LENGTH: 5,
  EMAIL_MAX_LENGTH: 255,
  EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,

  // Пароль
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_LENGTH: 128,
  PASSWORD_PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,

  // Имя пользователя
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 50,
  NAME_PATTERN: /^[a-zA-Zа-яА-ЯёЁ\s]+$/,

  // Телефон
  PHONE_PATTERN: /^\+?[\d\s\-\(\)]+$/,

  // URL
  URL_PATTERN: /^https?:\/\/.+/
} as const

/**
 * Настройки пагинации
 */
export const PAGINATION_SETTINGS = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  MAX_PAGE_NUMBER: 1000
} as const

/**
 * Настройки кеширования
 */
export const CACHE_SETTINGS = {
  // Время жизни кеша (в миллисекундах)
  USER_DATA_TTL: 300000, // 5 минут
  PERMISSIONS_TTL: 600000, // 10 минут
  TOKEN_DATA_TTL: 900000, // 15 минут

  // Максимальный размер кеша
  MAX_CACHE_SIZE: 50, // элементов

  // Настройки localStorage
  STORAGE_PREFIX: 'auth_',
  STORAGE_VERSION: '1.0'
} as const

/**
 * Настройки API
 */
export const API_SETTINGS = {
  // Базовый URL API
  BASE_URL: '/api',

  // Таймауты
  DEFAULT_TIMEOUT: 10000,
  UPLOAD_TIMEOUT: 30000,
  DOWNLOAD_TIMEOUT: 60000,

  // Количество повторных попыток
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,

  // Заголовки
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
} as const

/**
 * Настройки логирования
 */
export const LOGGING_SETTINGS = {
  // Уровни логирования
  LEVELS: {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3
  },

  // Максимальный размер лога
  MAX_LOG_SIZE: 1000,

  // Включить логирование в продакшене
  ENABLE_PRODUCTION_LOGGING: false
} as const

/**
 * Настройки безопасности
 */
export const SECURITY_SETTINGS = {
  // Двухфакторная аутентификация
  TWO_FACTOR_ISSUER: 'Vue.js App',

  // Шифрование
  ENCRYPTION_ALGORITHM: 'AES-GCM',
  KEY_LENGTH: 256,

  // Rate limiting
  MAX_LOGIN_ATTEMPTS: 5,
  LOCKOUT_DURATION: 900000, // 15 минут

  // Session
  SESSION_TIMEOUT: 3600000, // 1 час
  EXTEND_SESSION_ON_ACTIVITY: true
} as const

/**
 * Настройки интернационализации
 */
export const I18N_SETTINGS = {
  DEFAULT_LANGUAGE: 'ru',
  SUPPORTED_LANGUAGES: ['ru', 'en'],
  FALLBACK_LANGUAGE: 'ru',

  // Пространства имен
  NAMESPACES: {
    AUTH: 'auth',
    VALIDATION: 'validation',
    ERRORS: 'errors',
    COMMON: 'common'
  }
} as const

/**
 * Настройки файлов
 */
export const FILE_SETTINGS = {
  // Максимальный размер файла
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB

  // Разрешенные типы файлов
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_DOCUMENT_TYPES: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],

  // Качество изображений
  IMAGE_QUALITY: 0.8,
  THUMBNAIL_SIZE: 300
} as const

/**
 * Настройки уведомлений
 */
export const NOTIFICATION_SETTINGS = {
  // Длительность показа уведомлений
  DEFAULT_DURATION: 5000,
  ERROR_DURATION: 10000,
  SUCCESS_DURATION: 3000,

  // Максимальное количество уведомлений
  MAX_NOTIFICATIONS: 5,

  // Позиции уведомлений
  POSITIONS: {
    TOP_RIGHT: 'top-right',
    TOP_LEFT: 'top-left',
    BOTTOM_RIGHT: 'bottom-right',
    BOTTOM_LEFT: 'bottom-left',
    TOP_CENTER: 'top-center',
    BOTTOM_CENTER: 'bottom-center'
  }
} as const

/**
 * Настройки анимаций
 */
export const ANIMATION_SETTINGS = {
  // Длительность анимаций
  FAST_DURATION: 150,
  NORMAL_DURATION: 300,
  SLOW_DURATION: 500,

  // Easing функции
  EASING: {
    LINEAR: 'linear',
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out'
  }
} as const

/**
 * Настройки тестирования
 */
export const TESTING_SETTINGS = {
  // Моки API
  MOCK_API_DELAY: 500,
  MOCK_ERROR_RATE: 0.1,

  // Тестовые данные
  TEST_USER_EMAIL: 'test@example.com',
  TEST_USER_PASSWORD: 'testpassword123',

  // Настройки Vitest
  TEST_TIMEOUT: 10000,
  COVERAGE_THRESHOLD: 80
} as const