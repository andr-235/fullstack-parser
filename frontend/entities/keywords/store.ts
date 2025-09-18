import { create } from 'zustand';
import { keywordsApi } from './api';
import type {
  Keyword,
  CreateKeywordRequest,
  UpdateKeywordRequest,
  KeywordsFilters
} from './types';

interface KeywordsState {
  keywords: Keyword[];
  currentKeyword: Keyword | null;
  isLoading: boolean;
  error: string | null;
  total: number;

  // Actions
  fetchKeywords: (filters?: KeywordsFilters) => Promise<void>;
  fetchKeywordById: (id: number) => Promise<void>;
  createKeyword: (data: CreateKeywordRequest) => Promise<Keyword>;
  updateKeyword: (id: number, data: UpdateKeywordRequest) => Promise<Keyword>;
  deleteKeyword: (id: number) => Promise<void>;
  activateKeyword: (id: number) => Promise<Keyword>;
  deactivateKeyword: (id: number) => Promise<Keyword>;
  toggleKeywordStatus: (id: number, isActive: boolean) => Promise<Keyword>;
  clearError: () => void;
  setCurrentKeyword: (keyword: Keyword | null) => void;
}

export const useKeywordsStore = create<KeywordsState>((set, get) => ({
  keywords: [],
  currentKeyword: null,
  isLoading: false,
  error: null,
  total: 0,

  fetchKeywords: async (filters = {}) => {
    set({ isLoading: true, error: null });
    try {
      const keywords: Keyword[] = await keywordsApi.getKeywords(filters);
      set({
        keywords,
        total: keywords.length,
        isLoading: false
      });
    } catch (error: unknown) {
      let errorMessage = 'Ошибка загрузки ключевых слов';

      if (error instanceof Error) {
        if (error.message.includes('HTTP 503')) {
          errorMessage = 'Сервис временно недоступен. Повторите попытку позже.';
        } else if (error.message.includes('Network error')) {
          errorMessage = 'Проблема с подключением к сети. Проверьте интернет-соединение.';
        } else if (error.message.includes('HTTP 500')) {
          errorMessage = 'Внутренняя ошибка сервера. Попробуйте позже.';
        } else if (error.message.includes('HTTP 404')) {
          errorMessage = 'Ресурс не найден.';
        } else if (error.message.includes('HTTP 403')) {
          errorMessage = 'Доступ запрещен.';
        } else if (error.message.includes('HTTP 401')) {
          errorMessage = 'Необходима авторизация.';
        } else {
          errorMessage = error.message;
        }
      }

      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchKeywordById: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const keyword: Keyword = await keywordsApi.getKeyword(id);
      set({
        currentKeyword: keyword,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка загрузки ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  createKeyword: async (data: CreateKeywordRequest) => {
    set({ isLoading: true, error: null });
    try {
      const keyword: Keyword = await keywordsApi.createKeyword(data);
      const { keywords } = get();
      set({
        keywords: [keyword, ...keywords],
        isLoading: false
      });
      return keyword;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка создания ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  updateKeyword: async (id: number, data: UpdateKeywordRequest) => {
    set({ isLoading: true, error: null });
    try {
      const keyword: Keyword = await keywordsApi.updateKeyword(id, data);
      const { keywords } = get();
      const updatedKeywords = keywords.map(k => k.id === id ? keyword : k);
      set({
        keywords: updatedKeywords,
        currentKeyword: keyword,
        isLoading: false
      });
      return keyword;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка обновления ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteKeyword: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await keywordsApi.deleteKeyword(id);
      const { keywords } = get();
      const filteredKeywords = keywords.filter(k => k.id !== id);
      set({
        keywords: filteredKeywords,
        currentKeyword: null,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка удаления ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  activateKeyword: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const keyword: Keyword = await keywordsApi.activateKeyword(id);
      const { keywords } = get();
      const updatedKeywords = keywords.map(k => k.id === id ? keyword : k);
      set({
        keywords: updatedKeywords,
        currentKeyword: keyword,
        isLoading: false
      });
      return keyword;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка активации ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deactivateKeyword: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      const keyword: Keyword = await keywordsApi.deactivateKeyword(id);
      const { keywords } = get();
      const updatedKeywords = keywords.map(k => k.id === id ? keyword : k);
      set({
        keywords: updatedKeywords,
        currentKeyword: keyword,
        isLoading: false
      });
      return keyword;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка деактивации ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  toggleKeywordStatus: async (id: number, isActive: boolean) => {
    set({ isLoading: true, error: null });
    try {
      const keyword: Keyword = await keywordsApi.toggleKeywordStatus(id, isActive);
      const { keywords } = get();
      const updatedKeywords = keywords.map(k => k.id === id ? keyword : k);
      set({
        keywords: updatedKeywords,
        currentKeyword: keyword,
        isLoading: false
      });
      return keyword;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка изменения статуса ключевого слова';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentKeyword: (keyword: Keyword | null) => {
    set({ currentKeyword: keyword });
  },
}));