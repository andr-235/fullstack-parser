/**
 * Основной модуль аутентификации
 * Экспортирует все компоненты, сервисы, хранилища и утилиты
 */

// Типы и интерфейсы
export * from "./types";

// Сервисы
export * from "./services";

// Хранилища
export * from "./stores";

// Guards для роутов
export * from "./guards";

// Middleware
export * from "./middleware";

// Компоненты
export * from "./components";

// Утилиты
export * from "./utils";

/**
 * Функция для инициализации модуля аутентификации
 * Должна вызываться в main.ts приложения
 */
export async function initializeAuth(): Promise<void> {
  console.log("Инициализация модуля аутентификации...");
  console.log("DEBUG: Начало инициализации auth модуля");

  try {
    // Проверяем доступность модулей перед импортом
    console.log("DEBUG: Проверка доступности error.handler модуля");
    const errorHandlerModule = await import("./utils/error.handler");
    console.log("DEBUG: error.handler модуль загружен:", Object.keys(errorHandlerModule));

    // Инициализируем обработчик ошибок
    console.log("DEBUG: Инициализация error handler");
    const { initializeErrorHandler } = errorHandlerModule;
    console.log("DEBUG: initializeErrorHandler функция получена:", typeof initializeErrorHandler);
    initializeErrorHandler();
    console.log("DEBUG: Error handler инициализирован успешно");

    // Проверяем доступность middleware модуля
    console.log("DEBUG: Проверка доступности token.middleware модуля");
    const tokenMiddlewareModule = await import("./middleware/token.middleware");
    console.log("DEBUG: token.middleware модуль загружен:", Object.keys(tokenMiddlewareModule));

    // Инициализируем middleware для токенов
    console.log("DEBUG: Инициализация token middleware");
    const { initializeTokenMiddleware } = tokenMiddlewareModule;
    console.log("DEBUG: initializeTokenMiddleware функция получена:", typeof initializeTokenMiddleware);
    initializeTokenMiddleware({
      refreshThreshold: 5 * 60 * 1000, // 5 минут до истечения
      checkInterval: 60 * 1000, // Проверка каждую минуту
      maxRetryAttempts: 3,
      retryDelay: 1000
    });
    console.log("DEBUG: Token middleware инициализирован успешно");

    console.log("Модуль аутентификации инициализирован");
    console.log("DEBUG: Инициализация auth модуля завершена успешно");
  } catch (error) {
    console.error("DEBUG: Ошибка при инициализации auth модуля:", error);
    console.error("DEBUG: Stack trace:", error instanceof Error ? error.stack : 'No stack trace');
    throw error;
  }
}

import { getTokenMiddleware } from "./middleware/token.middleware";

/**
 * Функция для запуска middleware токенов
 * Должна вызываться после инициализации аутентификации
 */
export function startTokenMiddleware(): void {
  const middleware = getTokenMiddleware();

  if (middleware) {
    middleware.start();
    console.log("Middleware токенов запущен");
  }
}

/**
 * Функция для остановки middleware токенов
 * Должна вызываться перед выходом из приложения
 */
export function stopTokenMiddleware(): void {
  const middleware = getTokenMiddleware();

  if (middleware) {
    middleware.stop();
    console.log("Middleware токенов остановлен");
  }
}

import { useAuthStore } from "./stores";
import { useErrorHandler } from "./utils/error.handler";
import { createProtectedRoute, createGuestRoute, createPermissionRoute } from "./guards";

/**
 * Хелпер функция для проверки аутентификации в компонентах
 */
export function useAuth() {
  return {
    authStore: useAuthStore(),
    errorHandler: useErrorHandler()
  };
}

/**
 * Хелпер функция для создания защищенных роутов
 */
export function createAuthRoutes() {
  return {
    createProtectedRoute,
    createGuestRoute,
    createPermissionRoute
  };
}