// Совместимый API клиент для постепенной миграции
import { api } from './api'

// Экспортируем старый API для совместимости
export const apiService = {
  // VK Groups API
  getGroups: (params?: any) => api.get('/groups/', { params }),
  getGroup: (groupId: number) => api.get(`/groups/${groupId}`),
  getGroupStats: (groupId: number) => api.get(`/groups/${groupId}/stats`),
  createGroup: (groupData: any) => api.post('/groups/', groupData),
  updateGroup: (groupId: number, updateData: any) =>
    api.put(`/groups/${groupId}`, updateData),
  deleteGroup: (groupId: number) => api.delete(`/groups/${groupId}`),
  refreshGroupInfo: (groupId: number) => api.post(`/groups/${groupId}/refresh`),
  uploadGroupsFromFile: (file: File, options?: any) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.is_active !== undefined) {
      formData.append('is_active', options.is_active.toString())
    }
    if (options?.max_posts_to_check !== undefined) {
      formData.append(
        'max_posts_to_check',
        options.max_posts_to_check.toString()
      )
    }
    return api.post('/groups/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Keywords API
  getKeywords: (params?: any) => api.get('/keywords/', { params }),
  getKeyword: (keywordId: number) => api.get(`/keywords/${keywordId}`),
  createKeyword: (keywordData: any) => api.post('/keywords/', keywordData),
  updateKeyword: (keywordId: number, updateData: any) =>
    api.put(`/keywords/${keywordId}`, updateData),
  deleteKeyword: (keywordId: number) => api.delete(`/keywords/${keywordId}`),
  createKeywordsBulk: (keywordsData: any[]) =>
    api.post('/keywords/bulk/', keywordsData),
  getKeywordCategories: () => api.get('/keywords/categories'),
  uploadKeywordsFromFile: (file: File, options?: any) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.default_category) {
      formData.append('default_category', options.default_category)
    }
    if (options?.is_active !== undefined) {
      formData.append('is_active', options.is_active.toString())
    }
    if (options?.is_case_sensitive !== undefined) {
      formData.append('is_case_sensitive', options.is_case_sensitive.toString())
    }
    if (options?.is_whole_word !== undefined) {
      formData.append('is_whole_word', options.is_whole_word.toString())
    }
    return api.post('/keywords/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Comments API
  getComments: (params?: any) => api.get('/parser/comments', { params }),
  getCommentWithKeywords: (commentId: number) =>
    api.get(`/parser/comments/${commentId}`),
  updateCommentStatus: (commentId: number, statusUpdate: any) =>
    api.put(`/parser/comments/${commentId}/status`, statusUpdate),
  markCommentAsViewed: (commentId: number) =>
    api.post(`/parser/comments/${commentId}/view`),
  archiveComment: (commentId: number) =>
    api.post(`/parser/comments/${commentId}/archive`),
  unarchiveComment: (commentId: number) =>
    api.post(`/parser/comments/${commentId}/unarchive`),
  bulkMarkCommentsAsViewed: (commentIds: number[]) =>
    api.post('/parser/comments/bulk/mark-viewed', {
      comment_ids: commentIds,
    }),
  bulkArchiveComments: (commentIds: number[]) =>
    api.post('/parser/comments/bulk/archive', {
      comment_ids: commentIds,
    }),
  bulkUnarchiveComments: (commentIds: number[]) =>
    api.post('/parser/comments/bulk/unarchive', {
      comment_ids: commentIds,
    }),
  bulkDeleteComments: (commentIds: number[]) =>
    api.post('/parser/comments/bulk/delete', {
      comment_ids: commentIds,
    }),

  // Parser API
  startParser: (taskData: any) => api.post('/parser/parse', taskData),
  getParserState: () => api.get('/parser/state'),
  getParserStats: () => api.get('/parser/stats'),
  getRecentParseTasks: (params?: any) => api.get('/parser/tasks', { params }),
  stopParser: () => api.post('/parser/stop'),

  // Stats API
  getGlobalStats: () => api.get('/stats/global'),
  getDashboardStats: () => api.get('/stats/dashboard'),

  // Monitoring API
  getMonitoringStats: () => api.get('/monitoring/stats'),
  getMonitoringGroups: (params?: any) =>
    api.get('/monitoring/groups', { params }),
  getAvailableGroupsForMonitoring: (params?: any) =>
    api.get('/monitoring/groups/available', { params }),
  getActiveMonitoringGroups: (params?: any) =>
    api.get('/monitoring/groups/active', { params }),
  enableGroupMonitoring: (
    groupId: number,
    intervalMinutes: number = 60,
    priority: number = 5
  ) =>
    api.post(`/monitoring/groups/${groupId}/enable`, {
      interval_minutes: intervalMinutes,
      priority,
    }),
  disableGroupMonitoring: (groupId: number) =>
    api.post(`/monitoring/groups/${groupId}/disable`),
  updateGroupMonitoring: (groupId: number, updateData: any) =>
    api.put(`/monitoring/groups/${groupId}/settings`, updateData),
  runGroupMonitoring: (groupId: number) =>
    api.post(`/monitoring/groups/${groupId}/run`),
  runMonitoringCycle: () => api.post('/monitoring/run-cycle'),
  getSchedulerStatus: () => api.get('/monitoring/scheduler/status'),

  // Settings API
  getSettings: () => api.get('/settings/'),
  updateSettings: (settings: any) => api.put('/settings/', settings),
  resetSettings: () => api.post('/settings/reset'),
  getSettingsHealth: () => api.get('/settings/health'),

  // Error Reports API
  getErrorReports: (params?: any) => api.get('/errors/reports', { params }),
  getErrorReport: (reportId: string) => api.get(`/errors/reports/${reportId}`),
  getErrorStats: (days: number = 7) => api.get(`/errors/stats?days=${days}`),
  acknowledgeErrorReport: (reportId: string) =>
    api.post(`/errors/reports/${reportId}/acknowledge`),
  deleteErrorReport: (reportId: string) =>
    api.delete(`/errors/reports/${reportId}`),

  // Health check
  healthCheck: () => api.get('/'),

  // Dashboard/DashboardPage API
  getActivityData: (params: { timeRange: string }) =>
    api.get('/stats/activity', { params }),
  getTopGroups: (params: { limit: number }) =>
    api.get('/stats/top-groups', { params }),
  getTopKeywords: (params: { limit: number }) =>
    api.get('/stats/top-keywords', { params }),
  getRecentComments: (params: { limit: number }) =>
    api.get('/stats/recent-comments', { params }),
  getSystemStatus: () => api.get('/system/status'),
  getParsingProgress: () => api.get('/parser/progress'),
  getRecentActivity: (params: { limit: number }) =>
    api.get('/activity/recent', { params }),
}

// Утилиты для создания query keys
export const createQueryKey = {
  groups: (params?: any) => ['groups', params] as const,
  group: (id: number) => ['groups', id] as const,
  groupStats: (id: number) => ['groups', id, 'stats'] as const,
  keywords: (params?: any) => ['keywords', params] as const,
  keyword: (id: number) => ['keywords', id] as const,
  keywordCategories: () => ['keywords', 'categories'] as const,
  comments: (params?: any) => ['comments', params] as const,
  comment: (id: number) => ['comments', id] as const,
  parserState: () => ['parser', 'state'] as const,
  parserStats: () => ['parser', 'stats'] as const,
  parserRuns: () => ['parser', 'tasks'] as const,
  globalStats: () => ['stats', 'global'] as const,
  dashboardStats: () => ['stats', 'dashboard'] as const,
  monitoringStats: () => ['monitoring', 'stats'] as const,
  monitoringGroups: (params?: any) => ['monitoring', 'groups', params] as const,
  settings: () => ['settings'] as const,
  settingsHealth: () => ['settings', 'health'] as const,
  errorReports: (params?: any) => ['error-reports', params] as const,
  errorReport: (id: string) => ['error-reports', id] as const,
  errorStats: (days: number) => ['error-reports', 'stats', days] as const,
  systemStatus: () => ['system', 'status'] as const,
  parsingProgress: () => ['parser', 'progress'] as const,
  recentActivity: (limit: number) => ['activity', 'recent', limit] as const,

  // Dashboard query keys
  activityData: (timeRange: string) =>
    ['dashboard', 'activity', timeRange] as const,
  topGroups: (limit: number) => ['dashboard', 'top-groups', limit] as const,
  topKeywords: (limit: number) => ['dashboard', 'top-keywords', limit] as const,
  recentComments: (limit: number) =>
    ['dashboard', 'recent-comments', limit] as const,

  // Недостающие query keys для мониторинга
  availableGroupsForMonitoring: (params?: any) =>
    ['monitoring', 'groups', 'available', params] as const,
  activeMonitoringGroups: (params?: any) =>
    ['monitoring', 'groups', 'active', params] as const,
  schedulerStatus: () => ['monitoring', 'scheduler', 'status'] as const,
}
