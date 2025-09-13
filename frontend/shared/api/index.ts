// Re-export API client and utilities
export { httpClient } from '@/shared/lib/http-client'
export { commentsApi } from './comments'
export { groupsApi } from './groups'
export { keywordsApi } from './keywords'
export { parserApi } from './parser'
export { healthApi } from './health'

// Legacy export for backward compatibility
export { httpClient as apiClient } from '@/shared/lib/http-client'

// API endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    PROFILE: '/auth/profile',
  },

  // Keywords
  KEYWORDS: {
    LIST: '/keywords',
    CREATE: '/keywords',
    UPDATE: (id: string) => `/keywords/${id}`,
    DELETE: (id: string) => `/keywords/${id}`,
    SEARCH: '/keywords/search',
  },

  // Groups
  GROUPS: {
    LIST: '/groups',
    CREATE: '/groups',
    UPDATE: (id: string) => `/groups/${id}`,
    DELETE: (id: string) => `/groups/${id}`,
  },

  // Comments
  COMMENTS: {
    LIST: '/comments',
    CREATE: '/comments',
    UPDATE: (id: string) => `/comments/${id}`,
    DELETE: (id: string) => `/comments/${id}`,
    SEARCH: '/comments/search',
  },

  // Parser
  PARSER: {
    START: '/parser/start',
    STOP: '/parser/stop',
    STATUS: '/parser/status',
    RESULTS: '/parser/results',
  },

  // Monitoring
  MONITORING: {
    HEALTH: '/health',
    METRICS: '/metrics',
    LOGS: '/logs',
  },
} as const
