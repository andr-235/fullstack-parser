import { create } from 'zustand';
import { authorApi } from './api';
import { AxiosError } from 'axios';
import type {
  Author,
  AuthorCreateRequest,
  AuthorUpdateRequest,
  AuthorListResponse,
  AuthorFilters
} from './types';

interface AuthorState {
  authors: Author[];
  currentAuthor: Author | null;
  isLoading: boolean;
  error: string | null;
  total: number;

  // Actions
  fetchAuthors: (filters?: AuthorFilters) => Promise<void>;
  fetchAuthorById: (id: string) => Promise<void>;
  createAuthor: (data: AuthorCreateRequest) => Promise<Author>;
  updateAuthor: (id: string, data: AuthorUpdateRequest) => Promise<Author>;
  deleteAuthor: (id: string) => Promise<void>;
  fetchAuthorByVkId: (vkId: string) => Promise<void>;
  searchAuthors: (query: string, limit?: number) => Promise<void>;
  clearError: () => void;
  setCurrentAuthor: (author: Author | null) => void;
}

export const useAuthorStore = create<AuthorState>((set, get) => ({
  authors: [],
  currentAuthor: null,
  isLoading: false,
  error: null,
  total: 0,

  fetchAuthors: async (filters = {}) => {
    set({ isLoading: true, error: null });
    try {
      const response: AuthorListResponse = await authorApi.getAuthors(filters);
      set({
        authors: response.authors,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка загрузки авторов';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchAuthorById: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const author: Author = await authorApi.getAuthorById(id);
      set({
        currentAuthor: author,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка загрузки автора';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  createAuthor: async (data: AuthorCreateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const author: Author = await authorApi.createAuthor(data);
      const { authors } = get();
      set({
        authors: [author, ...authors],
        isLoading: false
      });
      return author;
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка создания автора';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  updateAuthor: async (id: string, data: AuthorUpdateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const author: Author = await authorApi.updateAuthor(id, data);
      const { authors } = get();
      const updatedAuthors = authors.map(a => a.id === id ? author : a);
      set({
        authors: updatedAuthors,
        currentAuthor: author,
        isLoading: false
      });
      return author;
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка обновления автора';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteAuthor: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await authorApi.deleteAuthor(id);
      const { authors } = get();
      const filteredAuthors = authors.filter(a => a.id !== id);
      set({
        authors: filteredAuthors,
        currentAuthor: null,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка удаления автора';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  fetchAuthorByVkId: async (vkId: string) => {
    set({ isLoading: true, error: null });
    try {
      const author: Author = await authorApi.getAuthorByVkId(vkId);
      set({
        currentAuthor: author,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка загрузки автора по VK ID';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  searchAuthors: async (query: string, limit = 20) => {
    set({ isLoading: true, error: null });
    try {
      const response: AuthorListResponse = await authorApi.searchAuthors(query, limit);
      set({
        authors: response.authors,
        total: response.total,
        isLoading: false
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof AxiosError && error.response?.data?.message ? error.response.data.message : error instanceof Error ? error.message : 'Ошибка поиска авторов';
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setCurrentAuthor: (author: Author | null) => {
    set({ currentAuthor: author });
  },
}));