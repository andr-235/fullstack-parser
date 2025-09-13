/**
 * API функции для аутентификации
 */

import { apiClient } from "@/shared/lib/api-client";
import type {
  LoginRequest,
  LoginResponse,
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
   * Вход в систему
   */
  async login(data: LoginRequest): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>("/auth/login", data);
  },

  /**
   * Обновить access токен
   */
  async refreshToken(data: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    return apiClient.post<RefreshTokenResponse>("/auth/refresh", data);
  },

  /**
   * Сменить пароль
   */
  async changePassword(data: ChangePasswordRequest): Promise<SuccessResponse> {
    return apiClient.post<SuccessResponse>("/auth/change-password", data);
  },

  /**
   * Запросить сброс пароля
   */
  async resetPassword(data: ResetPasswordRequest): Promise<SuccessResponse> {
    return apiClient.post<SuccessResponse>("/auth/reset-password", data);
  },

  /**
   * Подтвердить сброс пароля
   */
  async resetPasswordConfirm(data: ResetPasswordConfirmRequest): Promise<SuccessResponse> {
    return apiClient.post<SuccessResponse>("/auth/reset-password/confirm", data);
  },

  /**
   * Выход из системы
   */
  async logout(data: LogoutRequest): Promise<SuccessResponse> {
    return apiClient.post<SuccessResponse>("/auth/logout", data);
  },

  /**
   * Получить информацию о текущем пользователе
   */
  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>("/auth/me");
  },
};
