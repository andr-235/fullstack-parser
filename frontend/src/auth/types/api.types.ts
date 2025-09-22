/**
 * API типы для взаимодействия с бэкендом аутентификации
 */

import type { User, AuthTokens, AuthResponse } from './auth.types';

/**
 * Запрос на вход в систему
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Ответ при успешном входе в систему
 */
export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Запрос на регистрацию нового пользователя
 */
export interface RegisterRequest {
  email: string;
  password: string;
  fullName: string;
}

/**
 * Ответ при успешной регистрации
 */
export interface RegisterResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Запрос на обновление токена
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * Ответ при обновлении токена
 */
export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Запрос на смену пароля
 */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/**
 * Запрос на сброс пароля
 */
export interface ResetPasswordRequest {
  email: string;
}

/**
 * Запрос на подтверждение сброса пароля
 */
export interface ResetPasswordConfirmRequest {
  token: string;
  new_password: string;
}

/**
 * Запрос на выход из системы
 */
export interface LogoutRequest {
  refresh_token?: string;
}

/**
 * Успешный ответ API
 */
export interface SuccessResponse {
  success: boolean;
  message: string;
}

/**
 * Стандартный ответ API с данными
 */
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  success: boolean;
}

/**
 * Ошибка API
 */
export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
  timestamp?: string;
}

/**
 * Стандартный ответ с пагинацией
 */
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

/**
 * Параметры для пагинированных запросов
 */
export interface PaginationParams {
  page?: number;
  size?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * Фильтры для поиска
 */
export interface SearchFilters {
  query?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  [key: string]: any;
}

/**
 * Параметры запроса с пагинацией и фильтрами
 */
export interface QueryParams extends PaginationParams, SearchFilters {
  [key: string]: any;
}

/**
 * Метаданные для ответа API
 */
export interface ApiMetadata {
  timestamp: string;
  request_id: string;
  version: string;
  processing_time_ms: number;
}

/**
 * Полный ответ API с метаданными
 */
export interface ApiResponseWithMeta<T = any> extends ApiResponse<T> {
  meta: ApiMetadata;
}

/**
 * Параметры для загрузки файлов
 */
export interface FileUploadParams {
  file: File;
  field_name?: string;
  additional_data?: Record<string, any>;
}

/**
 * Прогресс загрузки файла
 */
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

/**
 * Настройки HTTP клиента
 */
export interface HttpClientConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  retryDelay: number;
  headers: Record<string, string>;
}

/**
 * Конфигурация для повторных попыток
 */
export interface RetryConfig {
  maxAttempts: number;
  delayMs: number;
  backoffMultiplier: number;
  retryCondition: (error: any) => boolean;
}

/**
 * Настройки для кеширования
 */
export interface CacheConfig {
  ttl: number;
  maxSize: number;
  storage: 'memory' | 'localStorage' | 'sessionStorage';
}

/**
 * Кешированный ответ
 */
export interface CachedResponse<T = any> {
  data: T;
  timestamp: number;
  expiresAt: number;
}