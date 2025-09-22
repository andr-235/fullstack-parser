import { useAuthStore } from "../stores/auth.store";

/**
 * Интерфейс для конфигурации middleware токенов
 */
export interface TokenMiddlewareConfig {
  /** Время в миллисекундах до истечения токена для начала обновления */
  refreshThreshold: number;
  /** Интервал проверки токенов в миллисекундах */
  checkInterval: number;
  /** Максимальное количество попыток обновления токена */
  maxRetryAttempts: number;
  /** Задержка между попытками обновления в миллисекундах */
  retryDelay: number;
}

/**
 * Интерфейс для состояния middleware
 */
export interface TokenMiddlewareState {
  isActive: boolean;
  nextRefreshTime: number | null;
  refreshTimer: number | null;
  checkTimer: number | null;
  retryCount: number;
  isRefreshing: boolean;
}

/**
 * Middleware для автоматического обновления токенов
 * Мониторит время жизни токенов и обновляет их перед истечением
 */
export class TokenMiddleware {
  private config: TokenMiddlewareConfig;
  private state: TokenMiddlewareState;
  private authStore: ReturnType<typeof useAuthStore>;

  constructor(config: Partial<TokenMiddlewareConfig> = {}) {
    this.config = {
      refreshThreshold: 5 * 60 * 1000, // 5 минут до истечения
      checkInterval: 60 * 1000, // Проверка каждую минуту
      maxRetryAttempts: 3,
      retryDelay: 1000,
      ...config
    };

    this.state = {
      isActive: false,
      nextRefreshTime: null,
      refreshTimer: null,
      checkTimer: null,
      retryCount: 0,
      isRefreshing: false
    };

    this.authStore = useAuthStore();
  }

  /**
   * Запускает middleware
   */
  public start(): void {
    if (this.state.isActive) {
      console.warn("TokenMiddleware уже запущен");
      return;
    }

    this.state.isActive = true;
    this.scheduleNextCheck();
    console.log("TokenMiddleware запущен");
  }

  /**
   * Останавливает middleware
   */
  public stop(): void {
    if (!this.state.isActive) {
      return;
    }

    this.state.isActive = false;
    this.clearTimers();
    console.log("TokenMiddleware остановлен");
  }

  /**
   * Принудительно обновляет токены
   */
  public async forceRefresh(): Promise<boolean> {
    if (!this.authStore.tokens?.refresh_token) {
      console.warn("Нет refresh токена для обновления");
      return false;
    }

    return this.performTokenRefresh();
  }

  /**
   * Получает текущее состояние middleware
   */
  public getState(): TokenMiddlewareState {
    return { ...this.state };
  }

  /**
   * Обновляет конфигурацию middleware
   */
  public updateConfig(config: Partial<TokenMiddlewareConfig>): void {
    const wasActive = this.state.isActive;

    if (wasActive) {
      this.stop();
    }

    this.config = { ...this.config, ...config };

    if (wasActive) {
      this.start();
    }
  }

  /**
   * Планирует следующую проверку токенов
   */
  private scheduleNextCheck(): void {
    if (!this.state.isActive) return;

    this.clearTimers();

    this.state.checkTimer = setTimeout(() => {
      this.checkTokens();
    }, this.config.checkInterval);
  }

  /**
   * Проверяет состояние токенов и планирует обновление
   */
  private checkTokens(): void {
    if (!this.state.isActive) return;

    const tokens = this.authStore.tokens;
    if (!tokens?.access_token) {
      this.scheduleNextCheck();
      return;
    }

    try {
      const tokenPayload = JSON.parse(atob(tokens.access_token.split(".")[1]));
      const expirationTime = tokenPayload.exp * 1000; // в миллисекундах
      const currentTime = Date.now();
      const timeUntilExpiry = expirationTime - currentTime;

      // Если токен истекает скоро, планируем обновление
      if (timeUntilExpiry <= this.config.refreshThreshold) {
        this.state.nextRefreshTime = currentTime + Math.max(timeUntilExpiry - 1000, 0);
        this.scheduleTokenRefresh();
      } else {
        // Обновляем время следующей проверки
        const nextCheckTime = Math.min(
          timeUntilExpiry - this.config.refreshThreshold + 1000,
          this.config.checkInterval
        );
        this.state.nextRefreshTime = currentTime + nextCheckTime;
      }
    } catch (error) {
      console.error("Ошибка при проверке токенов:", error);
    }

    this.scheduleNextCheck();
  }

  /**
   * Планирует обновление токенов
   */
  private scheduleTokenRefresh(): void {
    if (!this.state.isActive || !this.state.nextRefreshTime) return;

    this.clearTimers();

    const delay = Math.max(this.state.nextRefreshTime - Date.now(), 0);

    this.state.refreshTimer = setTimeout(() => {
      this.performTokenRefresh();
    }, delay);
  }

  /**
   * Выполняет обновление токенов
   */
  private async performTokenRefresh(): Promise<boolean> {
    if (this.state.isRefreshing) {
      console.log("Обновление токенов уже выполняется");
      return false;
    }

    if (!this.authStore.tokens?.refresh_token) {
      console.warn("Нет refresh токена для обновления");
      return false;
    }

    this.state.isRefreshing = true;
    this.state.retryCount = 0;

    try {
      console.log("Начинаем обновление токенов");
      const success = await this.retryTokenRefresh();

      if (success) {
        console.log("Токены успешно обновлены");
        this.state.retryCount = 0;
        return true;
      } else {
        console.error("Не удалось обновить токены после всех попыток");
        return false;
      }
    } finally {
      this.state.isRefreshing = false;
    }
  }

  /**
   * Выполняет обновление токенов с повторными попытками
   */
  private async retryTokenRefresh(): Promise<boolean> {
    while (this.state.retryCount < this.config.maxRetryAttempts) {
      try {
        const success = await this.authStore.refreshTokens();

        if (success) {
          return true;
        }
      } catch (error) {
        console.error(`Попытка обновления токенов ${this.state.retryCount + 1} не удалась:`, error);
      }

      this.state.retryCount++;

      if (this.state.retryCount < this.config.maxRetryAttempts) {
        console.log(`Повторная попытка через ${this.config.retryDelay}мс`);
        await this.delay(this.config.retryDelay);
      }
    }

    return false;
  }

  /**
   * Задержка выполнения
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Очищает все таймеры
   */
  private clearTimers(): void {
    if (this.state.refreshTimer) {
      clearTimeout(this.state.refreshTimer);
      this.state.refreshTimer = null;
    }

    if (this.state.checkTimer) {
      clearTimeout(this.state.checkTimer);
      this.state.checkTimer = null;
    }
  }
}

/**
 * Фабричная функция для создания middleware с конфигурацией по умолчанию
 */
export function createTokenMiddleware(config?: Partial<TokenMiddlewareConfig>): TokenMiddleware {
  return new TokenMiddleware(config);
}

/**
 * Глобальный экземпляр middleware для использования в приложении
 */
let globalMiddleware: TokenMiddleware | null = null;

/**
 * Инициализирует глобальный middleware
 */
export function initializeTokenMiddleware(config?: Partial<TokenMiddlewareConfig>): TokenMiddleware {
  if (globalMiddleware) {
    console.warn("TokenMiddleware уже инициализирован");
    return globalMiddleware;
  }

  globalMiddleware = new TokenMiddleware(config);
  return globalMiddleware;
}

/**
 * Получает глобальный экземпляр middleware
 */
export function getTokenMiddleware(): TokenMiddleware | null {
  return globalMiddleware;
}

/**
 * Composable для использования middleware в компонентах
 */
export function useTokenMiddleware(config?: Partial<TokenMiddlewareConfig>) {
  const middleware = new TokenMiddleware(config);

  return {
    middleware,
    start: () => middleware.start(),
    stop: () => middleware.stop(),
    forceRefresh: () => middleware.forceRefresh(),
    getState: () => middleware.getState(),
    updateConfig: (newConfig: Partial<TokenMiddlewareConfig>) =>
      middleware.updateConfig(newConfig)
  };
}