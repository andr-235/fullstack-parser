import { apiClient } from '@/shared/api/client';
import { AUTH_ROUTES, getRoutePath } from '@/shared/config/routes';
import type { LoginRequest, RegisterRequest, ChangePasswordRequest, ResetPasswordRequest, ResetPasswordConfirmRequest, AuthResponse, User } from '../types';

export const authApi = {
  async login(data: LoginRequest): Promise<AuthResponse> {
    console.log('[AuthAPI] Making login request to', getRoutePath(AUTH_ROUTES.LOGIN));
    console.log('[AuthAPI] Request data:', { email: data.email, password: '***' });
    try {
      const response = await apiClient.post<AuthResponse>(getRoutePath(AUTH_ROUTES.LOGIN), data);
      console.log('[AuthAPI] Login request successful');
      return response.data;
    } catch (error) {
      console.error('[AuthAPI] Login request failed:', error);
      throw error;
    }
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(getRoutePath(AUTH_ROUTES.REGISTER), data);
      return response.data;
    } catch (error) {
      console.error('[AuthAPI] Register request failed:', error);
      throw error;
    }
  },

  async changePassword(data: ChangePasswordRequest): Promise<void> {
    try {
      await apiClient.post(getRoutePath(AUTH_ROUTES.CHANGE_PASSWORD), data);
    } catch (error) {
      console.error('[AuthAPI] Change password request failed:', error);
      throw error;
    }
  },

  async refreshToken(): Promise<AuthResponse> {
    try {
      const response = await apiClient.post<AuthResponse>(getRoutePath(AUTH_ROUTES.REFRESH));
      return response.data;
    } catch (error) {
      console.error('[AuthAPI] Refresh token request failed:', error);
      throw error;
    }
  },

  async getCurrentUser(): Promise<User> {
    try {
      const response = await apiClient.get<User>(getRoutePath(AUTH_ROUTES.PROFILE));
      return response.data;
    } catch (error) {
      console.error('[AuthAPI] Get current user request failed:', error);
      throw error;
    }
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post(getRoutePath(AUTH_ROUTES.LOGOUT));
    } catch (error) {
      console.error('[AuthAPI] Logout request failed:', error);
      throw error;
    }
  },

  async resetPassword(data: ResetPasswordRequest): Promise<void> {
    try {
      await apiClient.post(getRoutePath(AUTH_ROUTES.RESET_PASSWORD), data);
    } catch (error) {
      console.error('[AuthAPI] Reset password request failed:', error);
      throw error;
    }
  },

  async resetPasswordConfirm(data: ResetPasswordConfirmRequest): Promise<void> {
    try {
      await apiClient.post(getRoutePath(AUTH_ROUTES.RESET_PASSWORD_CONFIRM), data);
    } catch (error) {
      console.error('[AuthAPI] Reset password confirm request failed:', error);
      throw error;
    }
  },
};