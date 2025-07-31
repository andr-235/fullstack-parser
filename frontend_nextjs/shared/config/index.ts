// API конфигурация с поддержкой runtime переменных
const getApiBaseUrl = () => {
  // В браузере используем window.location для определения базового URL
  if (typeof window !== 'undefined') {
    return `${window.location.protocol}//${window.location.host}`
  }
  // На сервере используем переменную окружения
  return process.env.NEXT_PUBLIC_API_URL || 'https://parser.mysite.ru'
}

export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
}

// Настройки приложения
export const APP_CONFIG = {
  name: 'Fullstack Parser',
  version: '1.0.0',
  description: 'Парсер контента ВКонтакте',
  author: 'Team',
}

// Настройки UI
export const UI_CONFIG = {
  theme: {
    default: 'dark' as const,
    options: ['light', 'dark', 'system'] as const,
  },
  pagination: {
    defaultPageSize: 20,
    pageSizeOptions: [10, 20, 50, 100],
  },
  refresh: {
    defaultInterval: 30, // секунды
    intervals: [15, 30, 60, 300],
  },
}

// Настройки мониторинга
export const MONITORING_CONFIG = {
  intervals: {
    fast: 30, // 30 секунд
    normal: 300, // 5 минут
    slow: 1800, // 30 минут
  },
  priorities: {
    high: 1,
    medium: 2,
    low: 3,
  },
}

// Настройки парсинга
export const PARSING_CONFIG = {
  maxPostsPerGroup: 1000,
  maxCommentsPerPost: 100,
  delayBetweenRequests: 1000, // миллисекунды
}

// Настройки уведомлений
export const NOTIFICATION_CONFIG = {
  duration: 5000, // миллисекунды
  position: 'top-right' as const,
  maxVisible: 5,
}

// Настройки кеширования
export const CACHE_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 минут
  gcTime: 10 * 60 * 1000, // 10 минут
  refetchOnWindowFocus: false,
  refetchOnReconnect: true,
}

export default {
  API_CONFIG,
  APP_CONFIG,
  UI_CONFIG,
  MONITORING_CONFIG,
  PARSING_CONFIG,
  NOTIFICATION_CONFIG,
  CACHE_CONFIG,
}
