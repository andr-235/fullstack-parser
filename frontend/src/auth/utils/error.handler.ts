import type { AuthError } from "../types";

// Константы типов ошибок
const AUTH_ERROR_TYPES = {
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  LOGIN_ERROR: 'LOGIN_ERROR',
  REGISTRATION_ERROR: 'REGISTRATION_ERROR',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  TOKEN_REFRESH_ERROR: 'TOKEN_REFRESH_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  UNAUTHORIZED_ERROR: 'UNAUTHORIZED_ERROR',
  FORBIDDEN: 'FORBIDDEN',
  FORBIDDEN_ERROR: 'FORBIDDEN_ERROR',
  USER_NOT_FOUND: 'USER_NOT_FOUND',
  WEAK_PASSWORD: 'WEAK_PASSWORD',
  EMAIL_ALREADY_EXISTS: 'EMAIL_ALREADY_EXISTS',
  PASSWORD_CHANGE_ERROR: 'PASSWORD_CHANGE_ERROR',
  PASSWORD_RESET_ERROR: 'PASSWORD_RESET_ERROR',
  PASSWORD_MISMATCH: 'PASSWORD_MISMATCH',
  INITIALIZATION_ERROR: 'INITIALIZATION_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
} as const;

type AuthErrorType = typeof AUTH_ERROR_TYPES[keyof typeof AUTH_ERROR_TYPES];

/**
 * Интерфейс для обработчика ошибок
 */
export interface ErrorHandler {
  handle(error: unknown): AuthError;
  log(error: AuthError): void;
  notify(error: AuthError): void;
  recover(error: AuthError): Promise<boolean>;
}

/**
 * Интерфейс для конфигурации обработчика ошибок
 */
export interface ErrorHandlerConfig {
  enableLogging: boolean;
  enableNotifications: boolean;
  enableRecovery: boolean;
  logLevel: "debug" | "info" | "warn" | "error";
  notificationDuration: number;
  maxRetryAttempts: number;
  retryDelay: number;
}

/**
 * Класс для обработки ошибок аутентификации
 * Предоставляет централизованную обработку всех ошибок аутентификации
 */
export class AuthErrorHandler implements ErrorHandler {
  private config: ErrorHandlerConfig;
  private errorMessages: Map<string, string>;

  constructor(config: Partial<ErrorHandlerConfig> = {}) {
    this.config = {
      enableLogging: true,
      enableNotifications: true,
      enableRecovery: true,
      logLevel: "error",
      notificationDuration: 5000,
      maxRetryAttempts: 3,
      retryDelay: 1000,
      ...config
    };

    this.errorMessages = this.initializeErrorMessages();
  }

  /**
   * Обрабатывает неизвестную ошибку и преобразует её в AuthError
   */
  public handle(error: unknown): AuthError {
    const authError = this.parseError(error);
    this.log(authError);
    this.notify(authError);
    return authError;
  }

  /**
   * Логирует ошибку аутентификации
   */
  public log(error: AuthError): void {
    if (!this.config.enableLogging) return;

    const logData = {
      type: error.type,
      code: error.code,
      message: error.message,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    switch (this.config.logLevel) {
      case "debug":
        console.debug("Auth Error:", logData);
        break;
      case "info":
        console.info("Auth Error:", logData);
        break;
      case "warn":
        console.warn("Auth Error:", logData);
        break;
      case "error":
        console.error("Auth Error:", logData);
        break;
    }
  }

  /**
   * Показывает уведомление пользователю об ошибке
   */
  public notify(error: AuthError): void {
    if (!this.config.enableNotifications) return;

    // Используем toast уведомления, если доступны
    if (typeof window !== "undefined" && (window as any).toast) {
      (window as any).toast.error(error.message, {
        duration: this.config.notificationDuration
      });
    } else {
      // Fallback на alert
      alert(`Ошибка аутентификации: ${error.message}`);
    }
  }

  /**
   * Попытка восстановления после ошибки
   */
  public async recover(error: AuthError): Promise<boolean> {
    if (!this.config.enableRecovery) return false;

    switch (error.type) {
      case "TOKEN_REFRESH_ERROR":
        return this.handleTokenRefreshError(error);
      case "NETWORK_ERROR":
        return this.handleNetworkError(error);
      case "VALIDATION_ERROR":
        return this.handleValidationError(error);
      default:
        return false;
    }
  }

  /**
   * Обновляет конфигурацию обработчика ошибок
   */
  public updateConfig(config: Partial<ErrorHandlerConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Добавляет пользовательское сообщение об ошибке
   */
  public addErrorMessage(code: string, message: string): void {
    this.errorMessages.set(code as AuthErrorType, message);
  }

  /**
   * Получает сообщение об ошибке по коду
   */
  public getErrorMessage(code: string): string {
    return this.errorMessages.get(code as AuthErrorType) || "Произошла неизвестная ошибка";
  }

  /**
   * Преобразует неизвестную ошибку в AuthError
   */
  private parseError(error: unknown): AuthError {
    // Если это уже AuthError, возвращаем как есть
    if (this.isAuthError(error)) {
      return {
        ...error,
        timestamp: new Date().toISOString()
      };
    }

    // Если это Error объект
    if (error instanceof Error) {
      return this.parseStandardError(error);
    }

    // Если это объект с полями
    if (typeof error === "object" && error !== null) {
      return this.parseObjectError(error);
    }

    // Если это строка
    if (typeof error === "string") {
      return this.parseStringError(error);
    }

    // Неизвестный тип ошибки
    return {
      type: AUTH_ERROR_TYPES.UNKNOWN_ERROR,
      message: "Произошла неизвестная ошибка",
      code: "UNKNOWN_ERROR",
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Проверяет, является ли объект AuthError
   */
  private isAuthError(error: unknown): error is AuthError {
    return (
      typeof error === "object" &&
      error !== null &&
      "type" in error &&
      "message" in error &&
      "code" in error
    );
  }

  /**
   * Обрабатывает стандартную Error
   */
  private parseStandardError(error: Error): AuthError {
    const message = error.message || "Произошла ошибка";

    // Определяем тип ошибки на основе сообщения
    if (message.includes("network") || message.includes("fetch")) {
      return {
        type: AUTH_ERROR_TYPES.NETWORK_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.NETWORK_ERROR),
        code: "NETWORK_ERROR",
        timestamp: new Date().toISOString()
      };
    }

    if (message.includes("401") || message.includes("unauthorized")) {
      return {
        type: AUTH_ERROR_TYPES.UNAUTHORIZED_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.UNAUTHORIZED_ERROR),
        code: "UNAUTHORIZED_ERROR",
        timestamp: new Date().toISOString()
      };
    }

    if (message.includes("403") || message.includes("forbidden")) {
      return {
        type: AUTH_ERROR_TYPES.FORBIDDEN_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.FORBIDDEN_ERROR),
        code: "FORBIDDEN_ERROR",
        timestamp: new Date().toISOString()
      };
    }

    return {
      type: AUTH_ERROR_TYPES.UNKNOWN_ERROR,
      message: message,
      code: "UNKNOWN_ERROR",
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Обрабатывает объект с полями ошибки
   */
  private parseObjectError(error: any): AuthError {
    const message = error.message || error.error || "Произошла ошибка";
    const code = error.code || error.status || "UNKNOWN_ERROR";

    // Определяем тип ошибки на основе кода или сообщения
    if (code === 401 || message.includes("unauthorized")) {
      return {
        type: AUTH_ERROR_TYPES.UNAUTHORIZED_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.UNAUTHORIZED_ERROR),
        code: code.toString(),
        timestamp: new Date().toISOString()
      };
    }

    if (code === 403 || message.includes("forbidden")) {
      return {
        type: AUTH_ERROR_TYPES.FORBIDDEN_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.FORBIDDEN_ERROR),
        code: code.toString(),
        timestamp: new Date().toISOString()
      };
    }

    if (code === 422 || message.includes("validation")) {
      return {
        type: AUTH_ERROR_TYPES.VALIDATION_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.VALIDATION_ERROR),
        code: code.toString(),
        timestamp: new Date().toISOString()
      };
    }

    if (code >= 500) {
      return {
        type: AUTH_ERROR_TYPES.SERVER_ERROR,
        message: this.getErrorMessage(AUTH_ERROR_TYPES.SERVER_ERROR),
        code: code.toString(),
        timestamp: new Date().toISOString()
      };
    }

    return {
      type: AUTH_ERROR_TYPES.UNKNOWN_ERROR,
      message: message,
      code: code.toString(),
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Обрабатывает строковую ошибку
   */
  private parseStringError(error: string): AuthError {
    return {
      type: AUTH_ERROR_TYPES.UNKNOWN_ERROR,
      message: error,
      code: "STRING_ERROR",
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Обрабатывает ошибку обновления токенов
   */
  private async handleTokenRefreshError(error: AuthError): Promise<boolean> {
    console.log("Попытка восстановления после ошибки обновления токенов");

    // Очищаем токены из localStorage
    localStorage.removeItem("auth_tokens");

    // Перенаправляем на страницу входа
    if (typeof window !== "undefined") {
      window.location.href = "/auth/login";
    }

    return true;
  }

  /**
   * Обрабатывает сетевую ошибку
   */
  private async handleNetworkError(error: AuthError): Promise<boolean> {
    console.log("Попытка восстановления после сетевой ошибки");

    // Проверяем подключение к интернету
    if (!navigator.onLine) {
      return false;
    }

    // Проверяем доступность API
    try {
      const response = await fetch("/api/health", {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });

      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Обрабатывает ошибку валидации
   */
  private async handleValidationError(error: AuthError): Promise<boolean> {
    console.log("Обработка ошибки валидации");

    // Для ошибок валидации восстановление не требуется
    // Просто показываем пользователю понятное сообщение
    return true;
  }

  /**
   * Инициализирует словарь сообщений об ошибках
   */
  private initializeErrorMessages(): Map<string, string> {
    const messages = new Map<string, string>();

    messages.set(AUTH_ERROR_TYPES.NETWORK_ERROR, "Ошибка сети. Проверьте подключение к интернету.");
    messages.set(AUTH_ERROR_TYPES.UNAUTHORIZED_ERROR, "Недостаточно прав доступа. Войдите в систему.");
    messages.set(AUTH_ERROR_TYPES.FORBIDDEN_ERROR, "Доступ запрещен.");
    messages.set(AUTH_ERROR_TYPES.VALIDATION_ERROR, "Ошибка валидации данных.");
    messages.set(AUTH_ERROR_TYPES.SERVER_ERROR, "Ошибка сервера. Попробуйте позже.");
    messages.set(AUTH_ERROR_TYPES.TOKEN_REFRESH_ERROR, "Сессия истекла. Войдите снова.");
    messages.set(AUTH_ERROR_TYPES.LOGIN_ERROR, "Ошибка входа. Проверьте email и пароль.");
    messages.set(AUTH_ERROR_TYPES.REGISTRATION_ERROR, "Ошибка регистрации. Попробуйте снова.");
    messages.set(AUTH_ERROR_TYPES.PASSWORD_CHANGE_ERROR, "Ошибка смены пароля.");
    messages.set(AUTH_ERROR_TYPES.PASSWORD_RESET_ERROR, "Ошибка сброса пароля.");
    messages.set(AUTH_ERROR_TYPES.INITIALIZATION_ERROR, "Ошибка инициализации. Перезагрузите страницу.");

    return messages;
  }
}

/**
 * Глобальный обработчик ошибок аутентификации
 */
let globalErrorHandler: AuthErrorHandler | null = null;

/**
 * Инициализирует глобальный обработчик ошибок
 */
export function initializeErrorHandler(config?: Partial<ErrorHandlerConfig>): AuthErrorHandler {
  if (globalErrorHandler) {
    console.warn("AuthErrorHandler уже инициализирован");
    return globalErrorHandler;
  }

  globalErrorHandler = new AuthErrorHandler(config);
  return globalErrorHandler;
}

/**
 * Получает глобальный обработчик ошибок
 */
export function getErrorHandler(): AuthErrorHandler | null {
  return globalErrorHandler;
}

/**
 * Обработка ошибки аутентификации с указанным типом
 * @param error Ошибка
 * @param type Тип ошибки
 * @throws AuthError с указанным типом
 */
export function handleAuthError(error: unknown, type: string): never {
  const handler = getErrorHandler() || new AuthErrorHandler();
  const authError = handler.handle(error);
  authError.type = type;
  authError.timestamp = new Date().toISOString();
  throw authError;
}

/**
 * Composable для использования обработчика ошибок в компонентах
 */
export function useErrorHandler(config?: Partial<ErrorHandlerConfig>) {
  const errorHandler = new AuthErrorHandler(config);

  return {
    handle: (error: unknown) => errorHandler.handle(error),
    log: (error: AuthError) => errorHandler.log(error),
    notify: (error: AuthError) => errorHandler.notify(error),
    recover: (error: AuthError) => errorHandler.recover(error),
    addErrorMessage: (code: string, message: string) =>
      errorHandler.addErrorMessage(code, message),
    getErrorMessage: (code: string) => errorHandler.getErrorMessage(code)
  };
}