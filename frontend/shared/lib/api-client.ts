/**
 * API клиент с интеграцией аутентификации
 */

import { HttpClient } from "./http-client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

// Создаем HTTP клиент с поддержкой авторизации
export const apiClient = new HttpClient(API_BASE_URL, () => {
  // Получаем токен из Zustand store
  if (typeof window !== 'undefined') {
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const parsed = JSON.parse(authStorage);
        return parsed.state?.accessToken || null;
      }
    } catch (error) {
      console.error('Error parsing auth storage:', error);
    }
  }
  return null;
});

// Экспортируем для обратной совместимости
export { apiClient as httpClient };
