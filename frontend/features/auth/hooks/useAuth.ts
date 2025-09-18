"use client";

import { useAuthStore } from "@/entities/user";
import { useEffect } from "react";

/**
 * Хук для работы с аутентификацией
 */
export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    register,
    login,
    logout,
    refreshAccessToken,
    clearError,
    setUser,
  } = useAuthStore();

  /**
   * Эффект для автоматического обновления токена доступа при инициализации.
   * Если пользователь аутентифицирован, но данные пользователя не загружены,
   * пытается обновить токен. В случае неудачи выполняет logout.
   */
  useEffect(() => {
    if (isAuthenticated && !user) {
      // Если пользователь аутентифицирован, но данные пользователя не загружены
      // загружаем их
      refreshAccessToken().catch(() => {
        // Если не удалось обновить токен, выходим из системы
        logout();
      });
    }
  }, [isAuthenticated, user, refreshAccessToken, logout]);

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    register,
    login,
    logout,
    refreshAccessToken,
    clearError,
    setUser,
  };
};
