// Совместимый API клиент для постепенной миграции
import { apiService, apiUtils } from './api'

// Экспортируем старый API для совместимости
export const api = {
  // VK Groups API
  getGroups: (params?: any) => apiService.get('/api/v1/groups/', { params }),
  getGroup: (groupId: number) => apiService.get(`/api/v1/groups/${groupId}`),
  getGroupStats: (groupId: number) =>
    apiService.get(`/api/v1/groups/${groupId}/stats`),
  createGroup: (groupData: any) =>
    apiService.post('/api/v1/groups/', groupData),
  updateGroup: (groupId: number, updateData: any) =>
    apiService.put(`/api/v1/groups/${groupId}`, updateData),
  deleteGroup: (groupId: number) =>
    apiService.delete(`/api/v1/groups/${groupId}`),
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
    return apiService.post('/api/v1/groups/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Keywords API
  getKeywords: (params?: any) =>
    apiService.get('/api/v1/keywords/', { params }),
  getKeyword: (keywordId: number) =>
    apiService.get(`/api/v1/keywords/${keywordId}`),
  createKeyword: (keywordData: any) =>
    apiService.post('/api/v1/keywords/', keywordData),
  updateKeyword: (keywordId: number, updateData: any) =>
    apiService.put(`/api/v1/keywords/${keywordId}`, updateData),
  deleteKeyword: (keywordId: number) =>
    apiService.delete(`/api/v1/keywords/${keywordId}`),
  createKeywordsBulk: (keywordsData: any[]) =>
    apiService.post('/api/v1/keywords/bulk/', keywordsData),
  getKeywordCategories: () => apiService.get('/api/v1/keywords/categories'),
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
    return apiService.post('/api/v1/keywords/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Comments API
  getComments: (params?: any) =>
    apiService.get('/api/v1/parser/comments', { params }),
  getCommentWithKeywords: (commentId: number) =>
    apiService.get(`/api/v1/parser/comments/${commentId}`),
  updateCommentStatus: (commentId: number, statusUpdate: any) =>
    apiService.put(`/api/v1/parser/comments/${commentId}/status`, statusUpdate),
  markCommentAsViewed: (commentId: number) =>
    apiService.post(`/api/v1/parser/comments/${commentId}/view`),
  archiveComment: (commentId: number) =>
    apiService.post(`/api/v1/parser/comments/${commentId}/archive`),
  unarchiveComment: (commentId: number) =>
    apiService.post(`/api/v1/parser/comments/${commentId}/unarchive`),
  bulkMarkCommentsAsViewed: (commentIds: number[]) =>
    apiService.post('/api/v1/parser/comments/bulk/mark-viewed', {
      comment_ids: commentIds,
    }),
  bulkArchiveComments: (commentIds: number[]) =>
    apiService.post('/api/v1/parser/comments/bulk/archive', {
      comment_ids: commentIds,
    }),
  bulkUnarchiveComments: (commentIds: number[]) =>
    apiService.post('/api/v1/parser/comments/bulk/unarchive', {
      comment_ids: commentIds,
    }),
  bulkDeleteComments: (commentIds: number[]) =>
    apiService.post('/api/v1/parser/comments/bulk/delete', {
      comment_ids: commentIds,
    }),

  // Parser API
  startParser: (taskData: any) =>
    apiService.post('/api/v1/parser/parse', taskData),
  getParserState: () => apiService.get('/api/v1/parser/state'),
  getParserStats: () => apiService.get('/api/v1/parser/stats'),
  getRecentParseTasks: (params?: any) =>
    apiService.get('/api/v1/parser/tasks', { params }),
  stopParser: () => apiService.post('/api/v1/parser/stop'),

  // Stats API
  getGlobalStats: () => apiService.get('/api/v1/stats/global'),
  getDashboardStats: () => apiService.get('/api/v1/stats/dashboard'),

  // Monitoring API
  getMonitoringStats: () => apiService.get('/api/v1/monitoring/stats'),
  getMonitoringGroups: (params?: any) =>
    apiService.get('/api/v1/monitoring/groups', { params }),
  getAvailableGroupsForMonitoring: (params?: any) =>
    apiService.get('/api/v1/monitoring/groups/available', { params }),
  getActiveMonitoringGroups: (params?: any) =>
    apiService.get('/api/v1/monitoring/groups/active', { params }),
  enableGroupMonitoring: (
    groupId: number,
    intervalMinutes: number = 60,
    priority: number = 5
  ) =>
    apiService.post(`/api/v1/monitoring/groups/${groupId}/enable`, {
      interval_minutes: intervalMinutes,
      priority,
    }),
  disableGroupMonitoring: (groupId: number) =>
    apiService.post(`/api/v1/monitoring/groups/${groupId}/disable`),
  updateGroupMonitoring: (groupId: number, updateData: any) =>
    apiService.put(`/api/v1/monitoring/groups/${groupId}/settings`, updateData),
  runGroupMonitoring: (groupId: number) =>
    apiService.post(`/api/v1/monitoring/groups/${groupId}/run`),
  runMonitoringCycle: () => apiService.post('/api/v1/monitoring/run-cycle'),
  getSchedulerStatus: () =>
    apiService.get('/api/v1/monitoring/scheduler/status'),

  // Settings API
  getSettings: () => apiService.get('/api/v1/settings/'),
  updateSettings: (settings: any) =>
    apiService.put('/api/v1/settings/', settings),
  resetSettings: () => apiService.post('/api/v1/settings/reset'),
  getSettingsHealth: () => apiService.get('/api/v1/settings/health'),

  // Error Reports API
  getErrorReports: (params?: any) =>
    apiService.get('/api/v1/errors/reports', { params }),
  getErrorReport: (reportId: string) =>
    apiService.get(`/api/v1/errors/reports/${reportId}`),
  getErrorStats: (days: number = 7) =>
    apiService.get(`/api/v1/errors/stats?days=${days}`),
  acknowledgeErrorReport: (reportId: string) =>
    apiService.post(`/api/v1/errors/reports/${reportId}/acknowledge`),
  deleteErrorReport: (reportId: string) =>
    apiService.delete(`/api/v1/errors/reports/${reportId}`),

  // Health check
  healthCheck: () => apiService.get('/api/v1/'),

  // Dashboard/DashboardPage API
  getActivityData: (params: { timeRange: string }) =>
    apiService.get('/api/v1/stats/activity', { params }),
  getTopGroups: (params: { limit: number }) =>
    apiService.get('/api/v1/stats/top-groups', { params }),
  getTopKeywords: (params: { limit: number }) =>
    apiService.get('/api/v1/stats/top-keywords', { params }),
  getRecentComments: (params: { limit: number }) =>
    apiService.get('/api/v1/stats/recent-comments', { params }),
  getSystemStatus: () => apiService.get('/api/v1/system/status'),
  getParsingProgress: () => apiService.get('/api/v1/parser/progress'),
  getRecentActivity: (params: { limit: number }) =>
    apiService.get('/api/v1/activity/recent', { params }),
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
}
