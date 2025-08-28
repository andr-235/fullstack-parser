// Application constants
export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  COMMENTS: '/comments',
  GROUPS: '/groups',
  KEYWORDS: '/keywords',
  MONITORING: '/monitoring',
  PARSER: '/parser',
  SETTINGS: '/settings',
} as const

export const API_ENDPOINTS = {
  COMMENTS: '/api/comments',
  GROUPS: '/api/groups',
  KEYWORDS: '/api/keywords',
  POSTS: '/api/posts',
  USERS: '/api/users',
} as const

export const LOCAL_STORAGE_KEYS = {
  USER: 'user',
  THEME: 'theme',
  SETTINGS: 'settings',
} as const
