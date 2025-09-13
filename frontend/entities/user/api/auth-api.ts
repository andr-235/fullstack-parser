/**
 * API функции для аутентификации
 */

import { httpClient } from "@/shared/lib/http-client";
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
  SuccessResponse,
  User,
} from "../model/types";

export const authApi = {
  /**
   * Регистрация нового пользователя
   */
  async register(data: RegisterRequest): Promise<RegisterResponse> {
    return httpClient.post<RegisterResponse>("/api/v1/auth/register", data);
  },

  /**
   * Вход в систему
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    return httpClient.post<LoginResponse>("/api/v1/auth/login", data);
  },

  /**
   * Обновить access токен
   */
  async refreshToken(data: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    return httpClient.post<RefreshTokenResponse>("/api/v1/auth/refresh", data);
  },

  /**
   * Сменить пароль
   */
  async changePassword(data: ChangePasswordRequest): Promise<SuccessResponse> {
    return httpClient.post<SuccessResponse>("/api/v1/auth/change-password", data);
  },

  /**
   * Запросить сброс пароля
   */
  async resetPassword(data: ResetPasswordRequest): Promise<SuccessResponse> {
    return httpClient.post<SuccessResponse>("/api/v1/auth/reset-password", data);
  },

  /**
   * Подтвердить сброс пароля
   */
  async resetPasswordConfirm(data: ResetPasswordConfirmRequest): Promise<SuccessResponse> {
    return httpClient.post<SuccessResponse>("/api/v1/auth/reset-password/confirm", data);
  },

  /**
   * Выход из системы
   */
  async logout(data: LogoutRequest): Promise<SuccessResponse> {
    return httpClient.post<SuccessResponse>("/api/v1/auth/logout", data);
  },

  /**
   * Получить информацию о текущем пользователе
   */
  async getCurrentUser(): Promise<User> {
    return httpClient.get<User>("/api/v1/auth/me");
  },
};
