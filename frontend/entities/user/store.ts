import { create } from 'zustand';
import { AuthStorage } from '@/shared/lib/auth-storage';
import { authApi } from './api';
import type { User, LoginRequest, RegisterRequest, AuthResponse } from './types';

// Константы для обработки ошибок
const DEFAULT_ERROR_MESSAGE = 'Произошла неизвестная ошибка';
const LOGIN_ERROR_MESSAGE = 'Ошибка входа';
const REGISTER_ERROR_MESSAGE = 'Ошибка регистрации';
const REFRESH_TOKEN_ERROR_MESSAGE = 'Ошибка обновления токена';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  accessToken: string | null;

  // Actions
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  accessToken: AuthStorage.getToken(),

  login: async (data: LoginRequest) => {
    set({ isLoading: true, error: null });
    try {
      console.log('[AuthStore] Attempting login with data:', { email: data.email, password: '***' });
      console.log('[AuthStore] Calling authApi.login...');
      const response: AuthResponse = await authApi.login(data);
      console.log('[AuthStore] Login successful, received tokens');
      AuthStorage.setToken(response.access_token);
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        accessToken: response.access_token
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : LOGIN_ERROR_MESSAGE;
      console.error('[AuthStore] Login failed:', errorMessage);
      console.error('[AuthStore] Full error object:', error);
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  register: async (data: RegisterRequest) => {
    set({ isLoading: true, error: null });
    try {
      const response: AuthResponse = await authApi.register(data);
      AuthStorage.setToken(response.access_token);
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
        accessToken: response.access_token
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : REGISTER_ERROR_MESSAGE;
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    set({ isLoading: true });
    try {
      await authApi.logout();
    } catch (error: unknown) {
      // Игнорируем ошибки при logout
      console.error('Logout error:', error);
    } finally {
      AuthStorage.removeToken();
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
        accessToken: null
      });
    }
  },

  refreshAccessToken: async () => {
    try {
      const response: AuthResponse = await authApi.refreshToken();
      AuthStorage.setToken(response.access_token);
      set({
        user: response.user,
        isAuthenticated: true,
        error: null,
        accessToken: response.access_token
      });
    } catch (error: unknown) {
      AuthStorage.removeToken();
      set({
        user: null,
        isAuthenticated: false,
        error: error instanceof Error ? error.message : REFRESH_TOKEN_ERROR_MESSAGE,
        accessToken: null
      });
      throw error;
    }
  },

  clearError: () => {
    set({ error: null });
  },

  setUser: (user: User | null) => {
    set({ user, isAuthenticated: !!user, accessToken: user ? get().accessToken : null });
  },
}));

// Инициализация store при загрузке приложения
if (typeof window !== 'undefined') {
  const token = AuthStorage.getToken();
  if (token) {
    // Попытка загрузить пользователя
    authApi.getCurrentUser()
      .then(user => {
        useAuthStore.getState().setUser(user);
      })
      .catch(() => {
        AuthStorage.removeToken();
        useAuthStore.setState({ user: null, isAuthenticated: false, accessToken: null });
      });
  }
}