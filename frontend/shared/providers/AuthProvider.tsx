"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/entities/user";
import { authApi } from "@/entities/user/api";

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const { setUser, isAuthenticated, accessToken } = useAuthStore();

  useEffect(() => {
    // При инициализации приложения проверяем, есть ли сохраненный токен
    if (isAuthenticated && accessToken) {
      // Загружаем информацию о пользователе
      authApi.getCurrentUser()
        .then(setUser)
        .catch(() => {
          // Если не удалось загрузить пользователя, очищаем состояние
          useAuthStore.getState().logout();
        });
    }
  }, [isAuthenticated, accessToken, setUser]);

  return <>{children}</>;
};