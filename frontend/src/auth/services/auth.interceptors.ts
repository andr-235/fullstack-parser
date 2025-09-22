/**
 * HTTP перехватчики для аутентификации
 */

import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { AuthTokens, AuthError } from '../types';
import type { ApiError } from '../types/api.types';
// Константы типов ошибок
const AUTH_ERROR_TYPES = {
  UNAUTHORIZED: 'UNAUTHORIZED',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR'
} as const;
import { AUTH_ERROR_CODES } from '../config';

/**
 * Класс для обработки HTTP перехватчиков аутентификации
 */
class AuthInterceptor {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Настройка перехватчиков запросов и ответов
   */
  private setupInterceptors(): void {
    // Перехватчик запросов - добавление токена авторизации
    this.api.interceptors.request.use(
      (config) => {
        const tokens = this.getStoredTokens();
        if (tokens?.access_token) {
          config.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Перехватчик ответов - обработка ошибок и обновление токенов
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !(originalRequest as any)._retry) {
          (originalRequest as any)._retry = true;
          return this.handleTokenRefresh(originalRequest);
        }

        return Promise.reject(this.transformError(error));
      }
    );
  }

  /**
   * Обработка обновления токена при 401 ошибке
   */
  private async handleTokenRefresh(originalRequest: any): Promise<any> {
    try {
      const tokens = this.getStoredTokens();
      if (!tokens?.refresh_token) {
        throw new Error('No refresh token available');
      }

      const response = await this.api.post('/auth/refresh', {
        refresh_token: tokens.refresh_token,
      });

      const newTokens = response.data;
      this.storeTokens(newTokens);

      // Повторяем оригинальный запрос с новым токеном
      originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
      return this.api(originalRequest);
    } catch (error) {
      this.clearTokens();
      window.location.href = '/login';
      return Promise.reject(error);
    }
  }

  /**
   * Преобразование ошибок API в стандартизированный формат
   */
  private transformError(error: AxiosError): AuthError {
    if (error.response && error.response.status === 401) {
      return {
        type: AUTH_ERROR_TYPES.UNAUTHORIZED,
        message: 'Неавторизованный доступ',
        details: error.response.data,
        timestamp: new Date().toISOString(),
      };
    }

    if (error.response && error.response.status === 422) {
      return {
        type: AUTH_ERROR_TYPES.VALIDATION_ERROR,
        message: (error.response.data as ApiError)?.detail || 'Ошибка валидации',
        details: error.response.data,
        timestamp: new Date().toISOString(),
      };
    }

    if (error.response && error.response.status >= 500) {
      return {
        type: AUTH_ERROR_TYPES.SERVER_ERROR,
        message: 'Ошибка сервера. Попробуйте позже.',
        details: error.response.data,
        timestamp: new Date().toISOString(),
      };
    }

    return {
      type: AUTH_ERROR_TYPES.NETWORK_ERROR,
      message: error.message || 'Произошла ошибка',
      details: error.response?.data,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Получение токенов из localStorage
   */
  private getStoredTokens(): AuthTokens | null {
    try {
      const stored = localStorage.getItem('auth_tokens');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  /**
   * Сохранение токенов в localStorage
   */
  private storeTokens(tokens: AuthTokens): void {
    try {
      localStorage.setItem('auth_tokens', JSON.stringify(tokens));
    } catch (error) {
      console.error('Failed to store tokens:', error);
    }
  }

  /**
   * Очистка токенов из localStorage
   */
  private clearTokens(): void {
    try {
      localStorage.removeItem('auth_tokens');
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }

  /**
   * Получение экземпляра axios для использования в сервисах
   */
  public getApi(): AxiosInstance {
    return this.api;
  }

  /**
   * Обновление базового URL API
   */
  public setBaseURL(url: string): void {
    this.api.defaults.baseURL = url;
  }

  /**
   * Обновление токенов вручную
   */
  public updateTokens(tokens: AuthTokens): void {
    this.storeTokens(tokens);
  }

  /**
   * Очистка токенов вручную
   */
  public clearStoredTokens(): void {
    this.clearTokens();
  }
}

// Экспорт синглтона
export const authInterceptor = new AuthInterceptor();