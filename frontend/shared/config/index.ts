// Конфигурация приложения
export const APP_CONFIG = {
  name: 'Fullstack Parser',
  version: '1.0.0',
  description: 'VK Social Media Content Parser',
} as const

// API конфигурация
export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  retries: 3,
} as const

// Пагинация
export const PAGINATION_CONFIG = {
  defaultPageSize: 20,
  maxPageSize: 100,
  pageSizeOptions: [10, 20, 50, 100],
} as const

// Кеширование
export const CACHE_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 минут
  cacheTime: 10 * 60 * 1000, // 10 минут
} as const

// Валидация
export const VALIDATION_CONFIG = {
  maxCommentLength: 1000,
  maxKeywordLength: 100,
  maxGroupNameLength: 200,
} as const

// UI конфигурация
export const UI_CONFIG = {
  theme: {
    primary: '#3b82f6',
    secondary: '#64748b',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
  },
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
} as const
