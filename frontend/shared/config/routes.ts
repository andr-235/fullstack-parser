// Конфигурация маршрутов приложения
// Определяет все API endpoints с типами доступа (public/private)

export type RouteType = 'public' | 'private'

export interface RouteConfig {
  path: string
  type: RouteType
  description?: string
}

// Базовые пути API
export const API_BASE = '/api'
export const API_V1_BASE = `${API_BASE}/v1`

// Маршруты аутентификации
export const AUTH_ROUTES = {
  // Публичные маршруты (не требуют аутентификации)
  LOGIN: { path: '/api/auth/login', type: 'public' as const, description: 'Вход в систему' },
  REGISTER: { path: '/api/auth/register', type: 'public' as const, description: 'Регистрация пользователя' },
  REFRESH: { path: '/api/auth/refresh', type: 'public' as const, description: 'Обновление токена' },
  RESET_PASSWORD: { path: '/api/auth/reset-password', type: 'public' as const, description: 'Запрос сброса пароля' },
  RESET_PASSWORD_CONFIRM: { path: '/api/auth/reset-password/confirm', type: 'public' as const, description: 'Подтверждение сброса пароля' },

  // Приватные маршруты (требуют аутентификации)
  LOGOUT: { path: '/api/auth/logout', type: 'private' as const, description: 'Выход из системы' },
  CHANGE_PASSWORD: { path: '/api/auth/change-password', type: 'private' as const, description: 'Смена пароля' },
  PROFILE: { path: '/api/auth/me', type: 'private' as const, description: 'Профиль пользователя' },
} as const

// Маршруты парсера
export const PARSER_ROUTES = {
  // Приватные маршруты
  PARSE: { path: '/api/parser/parse', type: 'private' as const, description: 'Запуск парсинга' },
  BULK_START: { path: '/api/parser/bulk-start', type: 'private' as const, description: 'Массовый запуск парсинга' },
  STOP: { path: '/api/parser/stop', type: 'private' as const, description: 'Остановка парсинга' },
  STATE: { path: '/api/parser/state', type: 'private' as const, description: 'Состояние парсера' },
  STATS: { path: '/api/parser/stats', type: 'private' as const, description: 'Статистика парсера' },
  GLOBAL_STATS: { path: '/api/parser/global-stats', type: 'private' as const, description: 'Глобальная статистика парсера' },
  TASKS: { path: '/api/parser/tasks', type: 'private' as const, description: 'Список задач' },
  TASK_STATUS: (taskId: string) => ({ path: `/api/parser/status/${taskId}`, type: 'private' as const, description: 'Статус задачи' }),
  HISTORY: { path: '/api/parser/history', type: 'private' as const, description: 'История парсинга' },
} as const

// Маршруты комментариев
export const COMMENTS_ROUTES = {
  // Приватные маршруты
  LIST: { path: '/api/v1/comments', type: 'private' as const, description: 'Список комментариев' },
  GET: (id: number) => ({ path: `/api/v1/comments/${id}`, type: 'private' as const, description: 'Получить комментарий' }),
  GET_BY_VK_ID: (vkId: number) => ({ path: `/api/v1/comments/vk/${vkId}`, type: 'private' as const, description: 'Комментарий по VK ID' }),
  CREATE: { path: '/api/v1/comments', type: 'private' as const, description: 'Создать комментарий' },
  UPDATE: (id: number) => ({ path: `/api/v1/comments/${id}`, type: 'private' as const, description: 'Обновить комментарий' }),
  DELETE: (id: number) => ({ path: `/api/v1/comments/${id}`, type: 'private' as const, description: 'Удалить комментарий' }),
  STATS: { path: '/api/v1/comments/stats/overview', type: 'private' as const, description: 'Статистика комментариев' },
  METRICS: { path: '/api/v1/comments/metrics', type: 'private' as const, description: 'Метрики комментариев' },

  // Анализ ключевых слов
  ANALYZE_KEYWORDS: { path: '/api/v1/comments/keyword-analysis/analyze', type: 'private' as const, description: 'Анализ ключевых слов' },
  ANALYZE_BATCH_KEYWORDS: { path: '/api/v1/comments/keyword-analysis/analyze-batch', type: 'private' as const, description: 'Массовый анализ ключевых слов' },
  SEARCH_BY_KEYWORDS: { path: '/api/v1/comments/keyword-analysis/search', type: 'private' as const, description: 'Поиск по ключевым словам' },
  KEYWORD_STATISTICS: { path: '/api/v1/comments/keyword-analysis/statistics', type: 'private' as const, description: 'Статистика ключевых слов' },

  // Действия с комментариями
  VIEW: (id: number) => ({ path: `/api/v1/comments/${id}/view`, type: 'private' as const, description: 'Отметить как просмотренный' }),
  ARCHIVE: (id: number) => ({ path: `/api/v1/comments/${id}/archive`, type: 'private' as const, description: 'Архивировать комментарий' }),
  UNARCHIVE: (id: number) => ({ path: `/api/v1/comments/${id}/unarchive`, type: 'private' as const, description: 'Разархивировать комментарий' }),
} as const

// Маршруты групп
export const GROUPS_ROUTES = {
  // Приватные маршруты
  LIST: { path: '/api/v1/groups', type: 'private' as const, description: 'Список групп' },
  GET: (id: number) => ({ path: `/api/v1/groups/${id}`, type: 'private' as const, description: 'Получить группу' }),
  CREATE: { path: '/api/v1/groups', type: 'private' as const, description: 'Создать группу' },
  UPDATE: (id: number) => ({ path: `/api/v1/groups/${id}`, type: 'private' as const, description: 'Обновить группу' }),
  DELETE: (id: number) => ({ path: `/api/v1/groups/${id}`, type: 'private' as const, description: 'Удалить группу' }),
  STATS: (id: number) => ({ path: `/api/v1/groups/${id}/stats`, type: 'private' as const, description: 'Статистика группы' }),
  GLOBAL_STATS: { path: '/api/v1/groups/stats', type: 'private' as const, description: 'Глобальная статистика групп' },
  METRICS: { path: '/api/v1/groups/metrics', type: 'private' as const, description: 'Метрики групп' },

  // Массовые операции
  BULK: { path: '/api/v1/groups/bulk', type: 'private' as const, description: 'Массовые операции с группами' },
  UPLOAD: { path: '/api/v1/groups/upload', type: 'private' as const, description: 'Загрузка групп' },
  UPLOAD_PROGRESS: (taskId: string) => ({ path: `/api/v1/groups/upload/${taskId}`, type: 'private' as const, description: 'Прогресс загрузки' }),
} as const

// Маршруты ключевых слов
export const KEYWORDS_ROUTES = {
  // Приватные маршруты
  LIST: { path: '/api/v1/keywords', type: 'private' as const, description: 'Список ключевых слов' },
  GET: (id: number) => ({ path: `/api/v1/keywords/${id}`, type: 'private' as const, description: 'Получить ключевое слово' }),
  CREATE: { path: '/api/v1/keywords', type: 'private' as const, description: 'Создать ключевое слово' },
  UPDATE: (id: number) => ({ path: `/api/v1/keywords/${id}`, type: 'private' as const, description: 'Обновить ключевое слово' }),
  DELETE: (id: number) => ({ path: `/api/v1/keywords/${id}`, type: 'private' as const, description: 'Удалить ключевое слово' }),
  SEARCH: { path: '/api/v1/keywords/search', type: 'private' as const, description: 'Поиск ключевых слов' },
  STATS: (id: number) => ({ path: `/api/v1/keywords/${id}/stats`, type: 'private' as const, description: 'Статистика ключевого слова' }),
  CATEGORIES: { path: '/api/v1/keywords/categories', type: 'private' as const, description: 'Категории ключевых слов' },
  METRICS: { path: '/api/v1/keywords/metrics', type: 'private' as const, description: 'Метрики ключевых слов' },

  // Массовые операции
  BULK: { path: '/api/v1/keywords/bulk', type: 'private' as const, description: 'Массовые операции с ключевыми словами' },
  UPLOAD: { path: '/api/v1/keywords/upload', type: 'private' as const, description: 'Загрузка ключевых слов' },
} as const

// Маршруты дашборда
export const DASHBOARD_ROUTES = {
  // Приватные маршруты
  METRICS: { path: '/api/v1/metrics/dashboard', type: 'private' as const, description: 'Метрики дашборда' },
  STATS: { path: '/api/dashboard/stats', type: 'private' as const, description: 'Статистика дашборда' },
} as const

// Маршруты здоровья системы
export const HEALTH_ROUTES = {
  // Публичные маршруты
  HEALTH: { path: '/api/v1/health', type: 'public' as const, description: 'Проверка здоровья' },
  DETAILED: { path: '/api/v1/health/detailed', type: 'public' as const, description: 'Детальная проверка здоровья' },
  READY: { path: '/api/v1/health/ready', type: 'public' as const, description: 'Проверка готовности' },
  LIVE: { path: '/api/v1/health/live', type: 'public' as const, description: 'Проверка живости' },
  STATUS: { path: '/api/v1/health/status', type: 'public' as const, description: 'Статус системы' },
} as const

// Все маршруты в одном объекте для удобства
export const ALL_ROUTES = {
  AUTH: AUTH_ROUTES,
  PARSER: PARSER_ROUTES,
  COMMENTS: COMMENTS_ROUTES,
  GROUPS: GROUPS_ROUTES,
  KEYWORDS: KEYWORDS_ROUTES,
  DASHBOARD: DASHBOARD_ROUTES,
  HEALTH: HEALTH_ROUTES,
} as const

// Утилиты для работы с маршрутами
export const getRoutePath = (route: RouteConfig | ((...args: any[]) => RouteConfig), ...args: any[]): string => {
  if (typeof route === 'function') {
    return route(...args).path
  }
  return route.path
}

export const getRouteType = (route: RouteConfig | ((...args: any[]) => RouteConfig), ...args: any[]): RouteType => {
  if (typeof route === 'function') {
    return route(...args).type
  }
  return route.type
}

export const isPublicRoute = (path: string): boolean => {
  // Проверяем, является ли маршрут публичным
  const allRoutes = Object.values(ALL_ROUTES).flatMap(module =>
    Object.values(module).filter(route => typeof route !== 'function')
  )

  return allRoutes.some(route => route.path === path && route.type === 'public')
}

export const isPrivateRoute = (path: string): boolean => {
  return !isPublicRoute(path)
}