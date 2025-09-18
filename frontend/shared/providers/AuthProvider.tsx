"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/entities/user";
import { authApi } from "@/entities/user/api";

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const { setUser, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    // При инициализации приложения проверяем, есть ли сохраненный токен
    if (isAuthenticated && !user) {
      // Загружаем информацию о пользователе
      authApi.getCurrentUser()
        .then(setUser)
        .catch(() => {
          // Если не удалось загрузить пользователя, очищаем состояние
          useAuthStore.getState().logout();
        });
    }
  }, [isAuthenticated, user, setUser]);

  return <>{children}</>;
};