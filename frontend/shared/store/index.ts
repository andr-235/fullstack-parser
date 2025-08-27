import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

/**
 * Типы для store
 */
interface AppSettings {
  theme: 'light' | 'dark' | 'system'
  sidebarCollapsed: boolean
  autoRefresh: boolean
  refreshInterval: number // в секундах
  itemsPerPage: number
  dateFormat: string
  showNotifications: boolean
}

interface UIState {
  // Модальные окна
  isCreateGroupModalOpen: boolean
  isCreateKeywordModalOpen: boolean
  isBulkKeywordModalOpen: boolean

  // Фильтры
  groupsFilter: {
    activeOnly: boolean
    searchTerm: string
  }
  keywordsFilter: {
    activeOnly: boolean
    category?: string
    searchTerm: string
  }
  commentsFilter: {
    groupId?: number
    keywordId?: number
    authorId?: number
    dateFrom?: string
    dateTo?: string
    searchTerm: string
  }

  // Выборка элементов
  selectedGroups: number[]
  selectedKeywords: number[]
  selectedComments: number[]
}

interface AppStore {
  // Настройки
  settings: AppSettings
  updateSettings: (settings: Partial<AppSettings>) => void
  resetSettings: () => void

  // UI состояние
  ui: UIState
  updateUI: (ui: Partial<UIState>) => void
  resetUI: () => void

  // Модальные окна
  openModal: (
    modal: keyof Pick<
      UIState,
      | 'isCreateGroupModalOpen'
      | 'isCreateKeywordModalOpen'
      | 'isBulkKeywordModalOpen'
    >
  ) => void
  closeModal: (
    modal: keyof Pick<
      UIState,
      | 'isCreateGroupModalOpen'
      | 'isCreateKeywordModalOpen'
      | 'isBulkKeywordModalOpen'
    >
  ) => void
  closeAllModals: () => void

  // Фильтры
  updateGroupsFilter: (filter: Partial<UIState['groupsFilter']>) => void
  updateKeywordsFilter: (filter: Partial<UIState['keywordsFilter']>) => void
  updateCommentsFilter: (filter: Partial<UIState['commentsFilter']>) => void
  resetFilters: () => void

  // Выборка
  selectGroup: (id: number) => void
  unselectGroup: (id: number) => void
  selectAllGroups: (ids: number[]) => void
  clearGroupSelection: () => void

  selectKeyword: (id: number) => void
  unselectKeyword: (id: number) => void
  selectAllKeywords: (ids: number[]) => void
  clearKeywordSelection: () => void

  selectComment: (id: number) => void
  unselectComment: (id: number) => void
  selectAllComments: (ids: number[]) => void
  clearCommentSelection: () => void

  // Утилиты
  clearAllSelections: () => void
}

/**
 * Дефолтные настройки
 */
const defaultSettings: AppSettings = {
  theme: 'system',
  sidebarCollapsed: false,
  autoRefresh: true,
  refreshInterval: 30,
  itemsPerPage: 20,
  dateFormat: 'dd.MM.yyyy HH:mm',
  showNotifications: true,
}

const defaultUI: UIState = {
  isCreateGroupModalOpen: false,
  isCreateKeywordModalOpen: false,
  isBulkKeywordModalOpen: false,

  groupsFilter: {
    activeOnly: true,
    searchTerm: '',
  },
  keywordsFilter: {
    activeOnly: true,
    searchTerm: '',
  },
  commentsFilter: {
    searchTerm: '',
  },

  selectedGroups: [],
  selectedKeywords: [],
  selectedComments: [],
}

/**
 * Основной store приложения
 */
export const useAppStore = create<AppStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Начальное состояние
        settings: defaultSettings,
        ui: defaultUI,

        // Методы для настроек
        updateSettings: (newSettings) =>
          set((state) => ({
            settings: { ...state.settings, ...newSettings },
          })),
        resetSettings: () =>
          set((state) => ({
            settings: { ...defaultSettings },
          })),

        // Методы для UI состояния
        updateUI: (newUI) =>
          set((state) => ({
            ui: { ...state.ui, ...newUI },
          })),
        resetUI: () =>
          set((state) => ({
            ui: { ...defaultUI },
          })),

        // Модальные окна
        openModal: (modal) =>
          set((state) => ({
            ui: {
              ...state.ui,
              [modal]: true,
            },
          })),
        closeModal: (modal) =>
          set((state) => ({
            ui: {
              ...state.ui,
              [modal]: false,
            },
          })),
        closeAllModals: () =>
          set((state) => ({
            ui: {
              ...state.ui,
              isCreateGroupModalOpen: false,
              isCreateKeywordModalOpen: false,
              isBulkKeywordModalOpen: false,
            },
          })),

        // Фильтры
        updateGroupsFilter: (filter) =>
          set((state) => ({
            ui: {
              ...state.ui,
              groupsFilter: { ...state.ui.groupsFilter, ...filter },
            },
          })),
        updateKeywordsFilter: (filter) =>
          set((state) => ({
            ui: {
              ...state.ui,
              keywordsFilter: { ...state.ui.keywordsFilter, ...filter },
            },
          })),
        updateCommentsFilter: (filter) =>
          set((state) => ({
            ui: {
              ...state.ui,
              commentsFilter: { ...state.ui.commentsFilter, ...filter },
            },
          })),
        resetFilters: () =>
          set((state) => ({
            ui: {
              ...state.ui,
              groupsFilter: { ...defaultUI.groupsFilter },
              keywordsFilter: { ...defaultUI.keywordsFilter },
              commentsFilter: { ...defaultUI.commentsFilter },
            },
          })),

        // Выборка групп
        selectGroup: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedGroups: [...state.ui.selectedGroups, id],
            },
          })),
        unselectGroup: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedGroups: state.ui.selectedGroups.filter(
                (groupId) => groupId !== id
              ),
            },
          })),
        selectAllGroups: (ids) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedGroups: ids,
            },
          })),
        clearGroupSelection: () =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedGroups: [],
            },
          })),

        // Выборка ключевых слов
        selectKeyword: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedKeywords: [...state.ui.selectedKeywords, id],
            },
          })),
        unselectKeyword: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedKeywords: state.ui.selectedKeywords.filter(
                (keywordId) => keywordId !== id
              ),
            },
          })),
        selectAllKeywords: (ids) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedKeywords: ids,
            },
          })),
        clearKeywordSelection: () =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedKeywords: [],
            },
          })),

        // Выборка комментариев
        selectComment: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedComments: [...state.ui.selectedComments, id],
            },
          })),
        unselectComment: (id) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedComments: state.ui.selectedComments.filter(
                (commentId) => commentId !== id
              ),
            },
          })),
        selectAllComments: (ids) =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedComments: ids,
            },
          })),
        clearCommentSelection: () =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedComments: [],
            },
          })),

        // Утилиты
        clearAllSelections: () =>
          set((state) => ({
            ui: {
              ...state.ui,
              selectedGroups: [],
              selectedKeywords: [],
              selectedComments: [],
            },
          })),
      }),
      {
        name: 'app-store',
        partialize: (state) => ({
          settings: state.settings,
          ui: {
            groupsFilter: state.ui.groupsFilter,
            keywordsFilter: state.ui.keywordsFilter,
            commentsFilter: state.ui.commentsFilter,
          },
        }),
      }
    ),
    {
      name: 'app-store',
    }
  )
)
