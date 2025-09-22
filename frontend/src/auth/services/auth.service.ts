/**
 * Сервис аутентификации для взаимодействия с API бэкенда
 */

import { authInterceptor } from './auth.interceptors';
import type {
  LoginRequest,
  LoginResponse,
  RegisterRequest,
  RegisterResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  ChangePasswordRequest,
  ResetPasswordRequest,
  ResetPasswordConfirmRequest,
  LogoutRequest,
  User,
  AuthTokens,
  AuthResponse,
  LoginCredentials,
  RegisterData,
  ChangePasswordData,
  ResetPasswordData,
  ResetPasswordConfirmData,
  LogoutData,
} from '../types';
// Константы типов ошибок
const AUTH_ERROR_TYPES = {
  UNAUTHORIZED: 'UNAUTHORIZED',
  LOGIN_ERROR: 'LOGIN_ERROR',
  REGISTRATION_ERROR: 'REGISTRATION_ERROR',
  TOKEN_REFRESH_ERROR: 'TOKEN_REFRESH_ERROR',
  PASSWORD_CHANGE_ERROR: 'PASSWORD_CHANGE_ERROR',
  PASSWORD_RESET_ERROR: 'PASSWORD_RESET_ERROR'
} as const;

import { TokenUtils } from '../utils/token.utils';
import { handleAuthError } from '../utils/error.handler';

/**
 * Сервис для работы с аутентификацией
 */
export class AuthService {
  private api = authInterceptor.getApi();

  /**
   * Вход в систему
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>('/auth/login', credentials);
    return response.data;
  }

  /**
   * Регистрация нового пользователя
   */
  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.api.post<RegisterResponse>('/auth/register', userData);
    return response.data;
  }

  /**
   * Обновление токена доступа
   */
  async refreshToken(tokens: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    const response = await this.api.post<RefreshTokenResponse>('/auth/refresh', tokens);
    return response.data;
  }

  /**
   * Смена пароля
   */
  async changePassword(data: ChangePasswordRequest): Promise<void> {
    await this.api.post('/auth/change-password', data);
  }

  /**
   * Запрос на сброс пароля
   */
  async resetPassword(email: ResetPasswordRequest): Promise<void> {
    await this.api.post('/auth/reset-password', email);
  }

  /**
   * Подтверждение сброса пароля
   */
  async resetPasswordConfirm(data: ResetPasswordConfirmRequest): Promise<void> {
    await this.api.post('/auth/reset-password-confirm', data);
  }

  /**
   * Выход из системы
   */
  async logout(data?: LogoutRequest): Promise<void> {
    await this.api.post('/auth/logout', data || {});
  }

  /**
   * Получение информации о текущем пользователе
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/auth/me');
    return response.data;
  }

  /**
   * Проверка валидности токена
   */
  async validateToken(): Promise<boolean> {
    try {
      await this.getCurrentUser();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Обновление токенов в хранилище
   */
  updateTokens(tokens: AuthTokens): void {
    authInterceptor.updateTokens(tokens);
  }

  /**
   * Очистка токенов из хранилища
   */
  clearTokens(): void {
    authInterceptor.clearStoredTokens();
  }

  /**
   * Настройка базового URL API
   */
  setBaseURL(url: string): void {
    authInterceptor.setBaseURL(url);
  }

  /**
   * Получение заголовков для авторизованных запросов
   */
  getAuthHeaders(): Record<string, string> {
    const tokens = this.getStoredTokens();
    return tokens?.access_token
      ? { Authorization: `Bearer ${tokens.access_token}` }
      : {};
  }

  /**
   * Получение сохраненных токенов
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
   * Получение текущего пользователя
   * @returns Пользователь или null, если токен недействителен или ошибка
   */
  static async getCurrentUser(): Promise<User | null> {
    const tokens = TokenUtils.loadTokens();
    if (!tokens || !TokenUtils.isTokenValid(tokens.access_token)) {
      return null;
    }

    try {
      const api = authInterceptor.getApi();
      const response = await api.get<User>('/auth/user', {
        headers: { Authorization: `Bearer ${tokens.access_token}` }
      });
      return response.data;
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.UNAUTHORIZED);
      return null;
    }
  }

  /**
   * Вход в систему
   * @param credentials Данные для входа
   * @returns Токены аутентификации
   */
  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const api = authInterceptor.getApi();
      const response = await api.post<LoginResponse>('/auth/login', credentials);
      TokenUtils.saveTokens({
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in
      });
      return {
        user: response.data.user,
        tokens: {
          access_token: response.data.access_token,
          refresh_token: response.data.refresh_token,
          token_type: response.data.token_type,
          expires_in: response.data.expires_in
        }
      };
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.LOGIN_ERROR);
    }
  }

  /**
   * Регистрация нового пользователя
   * @param data Данные для регистрации
   * @returns Токены аутентификации
   */
  static async register(data: RegisterData): Promise<AuthResponse> {
    try {
      const api = authInterceptor.getApi();
      const response = await api.post<RegisterResponse>('/auth/register', data);
      TokenUtils.saveTokens({
        access_token: response.data.access_token,
        refresh_token: response.data.refresh_token,
        token_type: response.data.token_type,
        expires_in: response.data.expires_in
      });
      return {
        user: response.data.user,
        tokens: {
          access_token: response.data.access_token,
          refresh_token: response.data.refresh_token,
          token_type: response.data.token_type,
          expires_in: response.data.expires_in
        }
      };
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.REGISTRATION_ERROR);
    }
  }

  /**
   * Выход из системы
   * @param data Опциональные данные для выхода (refresh_token)
   */
  static async logout(data?: LogoutData): Promise<void> {
    try {
      if (data?.refresh_token) {
        const api = authInterceptor.getApi();
        await api.post('/auth/logout', { refresh_token: data.refresh_token });
      }
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.TOKEN_REFRESH_ERROR);
    } finally {
      TokenUtils.clearTokens();
    }
  }

  /**
   * Обновление токена
   * @param request Запрос на обновление токена
   * @returns Новые токены
   */
  static async refreshToken(request: RefreshTokenRequest): Promise<AuthTokens> {
    try {
      const api = authInterceptor.getApi();
      const response = await api.post<AuthTokens>('/auth/refresh', request);
      TokenUtils.saveTokens(response.data);
      return response.data;
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.TOKEN_REFRESH_ERROR);
    }
  }

  /**
   * Смена пароля
   * @param data Данные для смены пароля
   */
  static async changePassword(data: ChangePasswordData): Promise<void> {
    try {
      const api = authInterceptor.getApi();
      await api.patch('/auth/change-password', data);
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.PASSWORD_CHANGE_ERROR);
    }
  }

  /**
   * Сброс пароля (отправка email)
   * @param data Данные для сброса (email)
   */
  static async resetPassword(data: ResetPasswordData): Promise<void> {
    try {
      const api = authInterceptor.getApi();
      await api.post('/auth/reset-password', data);
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.PASSWORD_RESET_ERROR);
    }
  }

  /**
   * Подтверждение сброса пароля
   * @param data Данные подтверждения (token, new_password)
   * @returns Токены аутентификации
   */
  static async confirmResetPassword(data: ResetPasswordConfirmData): Promise<AuthTokens> {
    try {
      const api = authInterceptor.getApi();
      const response = await api.post<AuthTokens>('/auth/reset-password/confirm', data);
      TokenUtils.saveTokens(response.data);
      return response.data;
    } catch (error) {
      handleAuthError(error, AUTH_ERROR_TYPES.PASSWORD_RESET_ERROR);
    }
  }
}

// Экспорт синглтона сервиса
export const authService = new AuthService();