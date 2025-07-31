// HTTP статусы
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
} as const

// Типы контента
export const CONTENT_TYPES = {
  COMMENT: 'comment',
  POST: 'post',
  GROUP: 'group',
  KEYWORD: 'keyword',
} as const

// Статусы парсинга
export const PARSING_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
} as const

// Фильтры
export const FILTER_TYPES = {
  ALL: 'all',
  POSITIVE: 'positive',
  NEGATIVE: 'negative',
  NEUTRAL: 'neutral',
} as const

// Сортировка
export const SORT_OPTIONS = {
  DATE_ASC: 'date_asc',
  DATE_DESC: 'date_desc',
  RELEVANCE: 'relevance',
  SENTIMENT: 'sentiment',
} as const

// Локальное хранилище ключи
export const STORAGE_KEYS = {
  THEME: 'theme',
  LANGUAGE: 'language',
  USER_PREFERENCES: 'user_preferences',
  AUTH_TOKEN: 'auth_token',
} as const

// Ограничения
export const LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  MAX_COMMENTS_PER_REQUEST: 1000,
  MAX_KEYWORDS_PER_GROUP: 50,
  MAX_GROUPS_PER_USER: 100,
} as const

// Форматы дат
export const DATE_FORMATS = {
  DISPLAY: 'dd.MM.yyyy HH:mm',
  API: 'yyyy-MM-dd HH:mm:ss',
  ISO: 'yyyy-MM-ddTHH:mm:ss.SSSZ',
} as const

// Регулярные выражения
export const REGEX = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  VK_URL: /^https?:\/\/(www\.)?vk\.com\//,
  PHONE: /^\+?[1-9]\d{1,14}$/,
} as const

// Сообщения об ошибках
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Ошибка сети. Проверьте подключение к интернету.',
  UNAUTHORIZED: 'Необходима авторизация.',
  FORBIDDEN: 'Доступ запрещен.',
  NOT_FOUND: 'Ресурс не найден.',
  VALIDATION_ERROR: 'Ошибка валидации данных.',
  SERVER_ERROR: 'Ошибка сервера. Попробуйте позже.',
  UNKNOWN_ERROR: 'Неизвестная ошибка.',
} as const

// Успешные сообщения
export const SUCCESS_MESSAGES = {
  SAVED: 'Данные успешно сохранены.',
  DELETED: 'Элемент успешно удален.',
  CREATED: 'Элемент успешно создан.',
  UPDATED: 'Данные успешно обновлены.',
} as const
