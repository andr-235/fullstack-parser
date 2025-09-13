"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/features/auth/hooks";

/**
 * Хук для управления доступом к маршрутам
 * Автоматически перенаправляет пользователей на нужные страницы
 */
export const useRouteAccess = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  // Публичные маршруты (доступны без авторизации)
  const publicRoutes = ["/login", "/reset-password"];
  
  // Приватные маршруты (требуют авторизации)
  const privateRoutes = ["/dashboard", "/profile", "/comments", "/groups", "/keywords", "/monitoring", "/parser", "/settings", "/change-password"];

  const isPublicRoute = publicRoutes.includes(pathname);
  const isPrivateRoute = privateRoutes.includes(pathname);

  useEffect(() => {
    if (isLoading) return; // Ждем загрузки состояния аутентификации

    if (isPublicRoute && isAuthenticated) {
      // Если пользователь авторизован и находится на публичной странице - перенаправляем на dashboard
      router.replace("/dashboard");
    } else if (isPrivateRoute && !isAuthenticated) {
      // Если пользователь не авторизован и пытается зайти на приватную страницу - перенаправляем на login
      router.replace("/login");
    } else if (pathname === "/" && !isLoading) {
      // Главная страница - перенаправляем в зависимости от статуса авторизации
      if (isAuthenticated) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }
  }, [isAuthenticated, isLoading, pathname, router, isPublicRoute, isPrivateRoute]);

  return {
    isAuthenticated,
    isLoading,
    isPublicRoute,
    isPrivateRoute,
  };
};
