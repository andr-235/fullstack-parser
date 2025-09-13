/**
 * Типы для пользователя и аутентификации
 */

import { ID, LoginRequest, BaseUser, AuthTokens } from '@/shared/types'

export type { LoginRequest }

export interface User extends BaseUser {
  full_name: string;
  is_superuser: boolean;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface RegisterResponse extends AuthTokens {
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface ResetPasswordRequest {
  email: string;
}

export interface ResetPasswordConfirmRequest {
  token: string;
  new_password: string;
}

export interface LogoutRequest {
  refresh_token: string;
}

export interface SuccessResponse {
  message: string;
}

export interface AuthError {
  message: string;
  status?: number;
}
