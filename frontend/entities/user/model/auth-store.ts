/**
 * Zustand store для управления состоянием аутентификации
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User, LoginRequest, RegisterRequest, AuthError } from "./types";
import { authApi } from "../api";

interface AuthState {
  // Состояние
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError | null;

  // Действия
  register: (data: RegisterRequest) => Promise<void>;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Начальное состояние
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Действия
      register: async (data: RegisterRequest) => {
        set({ isLoading: true, error: null });

        try {
          const response = await authApi.register(data);
          
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
            user: response.user,
          });
        } catch (error: any) {
          set({
            error: {
              message: error.message || "Ошибка регистрации",
              status: error.status,
            },
            isLoading: false,
          });
          throw error;
        }
      },

      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });

        try {
          const response = await authApi.login(credentials);
          
          set({
            accessToken: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
            user: response.user,
          });
        } catch (error: any) {
          set({
            error: {
              message: error.message || "Ошибка входа в систему",
              status: error.status,
            },
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        const { refreshToken } = get();
        
        // Отправляем запрос на logout если есть refresh token
        if (refreshToken) {
          authApi.logout({ refresh_token: refreshToken }).catch(console.error);
        }

        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        
        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        try {
          const response = await authApi.refreshToken({ refresh_token: refreshToken });
          
          set({
            accessToken: response.access_token,
            isAuthenticated: true,
            error: null,
          });
        } catch (error: any) {
          // Если refresh token недействителен, выходим из системы
          get().logout();
          throw error;
        }
      },

      clearError: () => {
        set({ error: null });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setUser: (user: User) => {
        set({ user });
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        user: state.user,
      }),
    }
  )
);
