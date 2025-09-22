/**
 * Экспорт всех типов аутентификации
 */

import type {
  User,
  AuthTokens,
  AuthResponse,
  AuthState,
  AuthError,
  LoginCredentials,
  RegisterData,
  ChangePasswordData,
  ResetPasswordData,
  ResetPasswordConfirmData,
  LogoutData,
  AuthConfig,
  AuthConfiguration,
} from './auth.types';

export type {
  User,
  AuthTokens,
  AuthResponse,
  AuthState,
  AuthError,
  LoginCredentials,
  RegisterData,
  ChangePasswordData,
  ResetPasswordData,
  ResetPasswordConfirmData,
  LogoutData,
  AuthConfig,
  AuthConfiguration,
} from './auth.types';

// Алиасы для удобства
export type AuthUser = User;
export type AuthTokenData = AuthTokens;
export type AuthErrorInfo = AuthError;
export type LoginFormData = LoginCredentials;
export type RegisterFormData = RegisterData;
export type ChangePasswordFormData = ChangePasswordData;
export type ResetPasswordFormData = ResetPasswordData;
export type ResetPasswordConfirmFormData = ResetPasswordConfirmData;
export type LogoutFormData = LogoutData;


// API типы
export type {
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
  ApiResponse,
  ApiError,
  PaginatedResponse,
  PaginationParams,
  SearchFilters,
  QueryParams,
  ApiMetadata,
  ApiResponseWithMeta,
  FileUploadParams,
  UploadProgress,
  HttpClientConfig,
  RetryConfig,
  CacheConfig,
  CachedResponse,
} from './api.types';
