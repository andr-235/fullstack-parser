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

        // Настройки
        updateSettings: (newSettings) =>
          set(
            (state) => ({
              settings: { ...state.settings, ...newSettings },
            }),
            false,
            'updateSettings'
          ),

        resetSettings: () =>
          set({ settings: defaultSettings }, false, 'resetSettings'),

        // UI состояние
        updateUI: (newUI) =>
          set(
            (state) => ({
              ui: { ...state.ui, ...newUI },
            }),
            false,
            'updateUI'
          ),

        resetUI: () => set({ ui: defaultUI }, false, 'resetUI'),

        // Модальные окна
        openModal: (modal) =>
          set(
            (state) => ({
              ui: { ...state.ui, [modal]: true },
            }),
            false,
            `openModal:${modal}`
          ),

        closeModal: (modal) =>
          set(
            (state) => ({
              ui: { ...state.ui, [modal]: false },
            }),
            false,
            `closeModal:${modal}`
          ),

        closeAllModals: () =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                isCreateGroupModalOpen: false,
                isCreateKeywordModalOpen: false,
                isBulkKeywordModalOpen: false,
              },
            }),
            false,
            'closeAllModals'
          ),

        // Фильтры
        updateGroupsFilter: (filter) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                groupsFilter: { ...state.ui.groupsFilter, ...filter },
              },
            }),
            false,
            'updateGroupsFilter'
          ),

        updateKeywordsFilter: (filter) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                keywordsFilter: { ...state.ui.keywordsFilter, ...filter },
              },
            }),
            false,
            'updateKeywordsFilter'
          ),

        updateCommentsFilter: (filter) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                commentsFilter: { ...state.ui.commentsFilter, ...filter },
              },
            }),
            false,
            'updateCommentsFilter'
          ),

        resetFilters: () =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                groupsFilter: defaultUI.groupsFilter,
                keywordsFilter: defaultUI.keywordsFilter,
                commentsFilter: defaultUI.commentsFilter,
              },
            }),
            false,
            'resetFilters'
          ),

        // Выборка групп
        selectGroup: (id) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedGroups: [...state.ui.selectedGroups, id],
              },
            }),
            false,
            'selectGroup'
          ),

        unselectGroup: (id) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedGroups: state.ui.selectedGroups.filter(
                  (gId) => gId !== id
                ),
              },
            }),
            false,
            'unselectGroup'
          ),

        selectAllGroups: (ids) =>
          set(
            (state) => ({
              ui: { ...state.ui, selectedGroups: ids },
            }),
            false,
            'selectAllGroups'
          ),

        clearGroupSelection: () =>
          set(
            (state) => ({
              ui: { ...state.ui, selectedGroups: [] },
            }),
            false,
            'clearGroupSelection'
          ),

        // Выборка ключевых слов
        selectKeyword: (id) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedKeywords: [...state.ui.selectedKeywords, id],
              },
            }),
            false,
            'selectKeyword'
          ),

        unselectKeyword: (id) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedKeywords: state.ui.selectedKeywords.filter(
                  (kId) => kId !== id
                ),
              },
            }),
            false,
            'unselectKeyword'
          ),

        selectAllKeywords: (ids) =>
          set(
            (state) => ({
              ui: { ...state.ui, selectedKeywords: ids },
            }),
            false,
            'selectAllKeywords'
          ),

        clearKeywordSelection: () =>
          set(
            (state) => ({
              ui: { ...state.ui, selectedKeywords: [] },
            }),
            false,
            'clearKeywordSelection'
          ),

        // Выборка комментариев
        selectComment: (id) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedComments: [...state.ui.selectedComments, id],
              },
            }),
            false,
            'selectComment'
          ),

        unselectComment: (id) =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedComments: state.ui.selectedComments.filter(
                  (cId) => cId !== id
                ),
              },
            }),
            false,
            'unselectComment'
          ),

        selectAllComments: (ids) =>
          set(
            (state) => ({
              ui: { ...state.ui, selectedComments: ids },
            }),
            false,
            'selectAllComments'
          ),

        clearCommentSelection: () =>
          set(
            (state) => ({
              ui: { ...state.ui, selectedComments: [] },
            }),
            false,
            'clearCommentSelection'
          ),

        // Утилиты
        clearAllSelections: () =>
          set(
            (state) => ({
              ui: {
                ...state.ui,
                selectedGroups: [],
                selectedKeywords: [],
                selectedComments: [],
              },
            }),
            false,
            'clearAllSelections'
          ),
      }),
      {
        name: 'vk-parser-store',
        partialize: (state) => ({ settings: state.settings }),
      }
    ),
    {
      name: 'app-store',
    }
  )
)

/**
 * Селекторы для оптимизации производительности
 */
export const selectSettings = (state: AppStore) => state.settings
export const selectUI = (state: AppStore) => state.ui
export const selectGroupsFilter = (state: AppStore) => state.ui.groupsFilter
export const selectKeywordsFilter = (state: AppStore) => state.ui.keywordsFilter
export const selectCommentsFilter = (state: AppStore) => state.ui.commentsFilter
export const selectSelectedGroups = (state: AppStore) => state.ui.selectedGroups
export const selectSelectedKeywords = (state: AppStore) =>
  state.ui.selectedKeywords
export const selectSelectedComments = (state: AppStore) =>
  state.ui.selectedComments
