import { create } from 'zustand'
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'

// Типы для состояния приложения
export interface AppState {
  // UI состояние
  ui: {
    theme: 'light' | 'dark' | 'system'
    sidebarCollapsed: boolean
    notifications: Notification[]
    loading: boolean
  }

  // Пользователь
  user: {
    id?: number
    email?: string
    name?: string
    isAuthenticated: boolean
    preferences: UserPreferences
  }

  // Фильтры и настройки
  filters: {
    comments: CommentFilters
    groups: GroupFilters
    keywords: KeywordFilters
  }

  // Кеш
  cache: {
    lastVisitedPages: string[]
    searchHistory: string[]
    recentGroups: number[]
  }
}

// Типы для уведомлений
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
  read: boolean
}

// Типы для пользовательских настроек
export interface UserPreferences {
  language: string
  timezone: string
  dateFormat: string
  pageSize: number
  autoRefresh: boolean
  notifications: {
    email: boolean
    browser: boolean
    sound: boolean
  }
}

// Типы для фильтров
export interface CommentFilters {
  status: 'all' | 'new' | 'viewed' | 'archived'
  sentiment: 'all' | 'positive' | 'negative' | 'neutral'
  dateRange: {
    from?: Date
    to?: Date
  }
  groups: number[]
  keywords: string[]
  search: string
}

export interface GroupFilters {
  status: 'all' | 'active' | 'inactive'
  monitoring: 'all' | 'enabled' | 'disabled'
  search: string
}

export interface KeywordFilters {
  category: 'all' | string
  status: 'all' | 'active' | 'inactive'
  search: string
}

// Действия для store
export interface AppActions {
  // UI действия
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  toggleSidebar: () => void
  addNotification: (
    notification: Omit<Notification, 'id' | 'timestamp' | 'read'>
  ) => void
  removeNotification: (id: string) => void
  markNotificationAsRead: (id: string) => void
  clearNotifications: () => void
  setLoading: (loading: boolean) => void

  // Пользовательские действия
  setUser: (user: Partial<AppState['user']>) => void
  logout: () => void
  updatePreferences: (preferences: Partial<UserPreferences>) => void

  // Действия с фильтрами
  setCommentFilters: (filters: Partial<CommentFilters>) => void
  resetCommentFilters: () => void
  setGroupFilters: (filters: Partial<GroupFilters>) => void
  resetGroupFilters: () => void
  setKeywordFilters: (filters: Partial<KeywordFilters>) => void
  resetKeywordFilters: () => void

  // Действия с кешем
  addToSearchHistory: (query: string) => void
  clearSearchHistory: () => void
  addToRecentGroups: (groupId: number) => void
  addToLastVisitedPages: (page: string) => void
}

// Начальное состояние
const initialState: AppState = {
  ui: {
    theme: 'system',
    sidebarCollapsed: false,
    notifications: [],
    loading: false,
  },
  user: {
    isAuthenticated: false,
    preferences: {
      language: 'ru',
      timezone: 'Europe/Moscow',
      dateFormat: 'dd.MM.yyyy HH:mm',
      pageSize: 20,
      autoRefresh: true,
      notifications: {
        email: true,
        browser: true,
        sound: false,
      },
    },
  },
  filters: {
    comments: {
      status: 'all',
      sentiment: 'all',
      dateRange: {},
      groups: [],
      keywords: [],
      search: '',
    },
    groups: {
      status: 'all',
      monitoring: 'all',
      search: '',
    },
    keywords: {
      category: 'all',
      status: 'all',
      search: '',
    },
  },
  cache: {
    lastVisitedPages: [],
    searchHistory: [],
    recentGroups: [],
  },
}

// Создание store
export const useAppStore = create<AppState & AppActions>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get) => ({
          ...initialState,

          // UI действия
          setTheme: (theme) =>
            set((state) => {
              state.ui.theme = theme
            }),

          toggleSidebar: () =>
            set((state) => {
              state.ui.sidebarCollapsed = !state.ui.sidebarCollapsed
            }),

          addNotification: (notification) =>
            set((state) => {
              const newNotification: Notification = {
                ...notification,
                id: Date.now().toString(),
                timestamp: new Date(),
                read: false,
              }
              state.ui.notifications.unshift(newNotification)

              // Ограничиваем количество уведомлений
              if (state.ui.notifications.length > 50) {
                state.ui.notifications = state.ui.notifications.slice(0, 50)
              }
            }),

          removeNotification: (id) =>
            set((state) => {
              state.ui.notifications = state.ui.notifications.filter(
                (n: Notification) => n.id !== id
              )
            }),

          markNotificationAsRead: (id) =>
            set((state) => {
              const notification = state.ui.notifications.find(
                (n: Notification) => n.id === id
              )
              if (notification) {
                notification.read = true
              }
            }),

          clearNotifications: () =>
            set((state) => {
              state.ui.notifications = []
            }),

          setLoading: (loading) =>
            set((state) => {
              state.ui.loading = loading
            }),

          // Пользовательские действия
          setUser: (user) =>
            set((state) => {
              Object.assign(state.user, user)
            }),

          logout: () =>
            set((state) => {
              state.user = initialState.user
              state.ui.notifications = []
            }),

          updatePreferences: (preferences) =>
            set((state) => {
              Object.assign(state.user.preferences, preferences)
            }),

          // Действия с фильтрами
          setCommentFilters: (filters) =>
            set((state) => {
              Object.assign(state.filters.comments, filters)
            }),

          resetCommentFilters: () =>
            set((state) => {
              state.filters.comments = initialState.filters.comments
            }),

          setGroupFilters: (filters) =>
            set((state) => {
              Object.assign(state.filters.groups, filters)
            }),

          resetGroupFilters: () =>
            set((state) => {
              state.filters.groups = initialState.filters.groups
            }),

          setKeywordFilters: (filters) =>
            set((state) => {
              Object.assign(state.filters.keywords, filters)
            }),

          resetKeywordFilters: () =>
            set((state) => {
              state.filters.keywords = initialState.filters.keywords
            }),

          // Действия с кешем
          addToSearchHistory: (query) =>
            set((state) => {
              if (!state.cache.searchHistory.includes(query)) {
                state.cache.searchHistory.unshift(query)
                // Ограничиваем историю поиска
                if (state.cache.searchHistory.length > 20) {
                  state.cache.searchHistory = state.cache.searchHistory.slice(
                    0,
                    20
                  )
                }
              }
            }),

          clearSearchHistory: () =>
            set((state) => {
              state.cache.searchHistory = []
            }),

          addToRecentGroups: (groupId) =>
            set((state) => {
              const index = state.cache.recentGroups.indexOf(groupId)
              if (index > -1) {
                state.cache.recentGroups.splice(index, 1)
              }
              state.cache.recentGroups.unshift(groupId)
              // Ограничиваем количество недавних групп
              if (state.cache.recentGroups.length > 10) {
                state.cache.recentGroups = state.cache.recentGroups.slice(0, 10)
              }
            }),

          addToLastVisitedPages: (page) =>
            set((state) => {
              const index = state.cache.lastVisitedPages.indexOf(page)
              if (index > -1) {
                state.cache.lastVisitedPages.splice(index, 1)
              }
              state.cache.lastVisitedPages.unshift(page)
              // Ограничиваем количество страниц
              if (state.cache.lastVisitedPages.length > 10) {
                state.cache.lastVisitedPages =
                  state.cache.lastVisitedPages.slice(0, 10)
              }
            }),
        }))
      ),
      {
        name: 'app-store',
        partialize: (state) => ({
          ui: {
            theme: state.ui.theme,
            sidebarCollapsed: state.ui.sidebarCollapsed,
          },
          user: { preferences: state.user.preferences },
          filters: state.filters,
          cache: state.cache,
        }),
      }
    ),
    {
      name: 'app-store',
    }
  )
)

// Селекторы для оптимизации
export const useTheme = () => useAppStore((state) => state.ui.theme)
export const useSidebarCollapsed = () =>
  useAppStore((state) => state.ui.sidebarCollapsed)
export const useNotifications = () =>
  useAppStore((state) => state.ui.notifications)
export const useLoading = () => useAppStore((state) => state.ui.loading)
export const useUser = () => useAppStore((state) => state.user)
export const useUserPreferences = () =>
  useAppStore((state) => state.user.preferences)
export const useCommentFilters = () =>
  useAppStore((state) => state.filters.comments)
export const useGroupFilters = () =>
  useAppStore((state) => state.filters.groups)
export const useKeywordFilters = () =>
  useAppStore((state) => state.filters.keywords)
export const useSearchHistory = () =>
  useAppStore((state) => state.cache.searchHistory)
export const useRecentGroups = () =>
  useAppStore((state) => state.cache.recentGroups)
