import { create } from 'zustand';
import { parserApi } from './api';
import type { ParserState, ParserStats, ParserTask, StartParserRequest, StartBulkParserRequest, ParserGlobalStats, ParserResponse } from './types';

/**
 * Интерфейс хранилища парсера для управления состоянием и действиями.
 */
interface ParserStore {
  // State
  /** Текущее состояние парсера */
  state: ParserState | null;
  /** Статистика парсера */
  stats: ParserStats | null;
  /** Глобальная статистика парсера */
  globalStats: ParserGlobalStats | null;
  /** Список задач парсера */
  tasks: ParserTask[];
  /** Флаг, указывающий, запущен ли парсер */
  isRunning: boolean | null;
  /** Флаг загрузки данных */
  loading: boolean;
  /** Флаг обработки операции */
  processing: boolean;
  /** Сообщение об ошибке */
  error: string | null;

  // Actions
  /** Получить текущее состояние парсера */
  fetchState: () => Promise<void>;
  /** Получить статистику парсера */
  fetchStats: () => Promise<void>;
  /** Получить список задач парсера */
  fetchTasks: () => Promise<void>;
  /** Запустить парсер с заданными параметрами */
  startParser: (data: StartParserRequest) => Promise<void>;
  /** Запустить массовый парсер с заданными параметрами */
  startBulkParser: (data: StartBulkParserRequest) => Promise<ParserResponse>;
  /** Остановить парсер */
  stopParser: () => Promise<void>;
  /** Перезагрузить все данные */
  refetch: () => Promise<void>;
  /** Очистить сообщение об ошибке */
  clearError: () => void;
}

export const useParserStore = create<ParserStore>((set, get) => ({
  // Initial state
  state: null,
  stats: null,
  globalStats: null,
  tasks: [],
  isRunning: false,
  loading: false,
  processing: false,
  error: null,

  // Actions
  fetchState: async () => {
    try {
      const state = await parserApi.getState();
      set({ state, isRunning: state.is_running });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch parser state';
      set({ error: errorMessage });
    }
  },

  fetchStats: async () => {
    try {
      const stats = await parserApi.getStats();
      // TODO: Implement proper global stats API endpoint
      const globalStats: ParserGlobalStats = {
        total_posts_found: 0, // TODO: Get from separate endpoint
        completed_tasks: stats.completed_tasks,
        failed_tasks: stats.failed_tasks,
        average_task_duration: 0,
        last_activity: new Date().toISOString(), // Используем текущее время как дефолт
        is_running: false, // Дефолтное значение, будет обновлено из состояния
        total_comments_found: 0, // TODO: Get from separate endpoint
      };
      set({ stats, globalStats });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch parser stats';
      set({ error: errorMessage });
    }
  },

  fetchTasks: async () => {
    try {
      const tasks = await parserApi.getTasks();
      set({ tasks });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch parser tasks';
      set({ error: errorMessage });
    }
  },

  startParser: async (data: StartParserRequest) => {
    set({ processing: true, error: null });
    try {
      await parserApi.startParser(data);
      await get().refetch();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start parser';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ processing: false });
    }
  },

  startBulkParser: async (data: StartBulkParserRequest) => {
    set({ processing: true, error: null });
    try {
      const result = await parserApi.startBulkParser(data);
      await get().refetch();
      return result;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start bulk parser';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ processing: false });
    }
  },

  stopParser: async () => {
    set({ processing: true, error: null });
    try {
      await parserApi.stopParser();
      await get().refetch();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to stop parser';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ processing: false });
    }
  },

  refetch: async () => {
    set({ loading: true });
    try {
      await Promise.all([
        get().fetchState(),
        get().fetchStats(),
        get().fetchTasks(),
      ]);
    } finally {
      set({ loading: false });
    }
  },

  clearError: () => {
    set({ error: null });
  },
}));