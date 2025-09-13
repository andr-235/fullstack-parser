/**
 * Сервис для управления токенами аутентификации
 * Инкапсулирует логику получения/сохранения токенов с обработкой SSR
 */
class AuthStorage {
  private static readonly TOKEN_KEY = 'auth_token';

  /**
   * Получить токен из хранилища
   * @returns токен или null, если не найден или на сервере
   */
  static getToken(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * Сохранить токен в хранилище
   * @param token токен для сохранения
   */
  static setToken(token: string): void {
    if (typeof window === 'undefined') {
      return;
    }
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  /**
   * Удалить токен из хранилища
   */
  static removeToken(): void {
    if (typeof window === 'undefined') {
      return;
    }
    localStorage.removeItem(this.TOKEN_KEY);
  }
}

export { AuthStorage };