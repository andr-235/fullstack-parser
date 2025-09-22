/**
 * Основные типы для системы аутентификации
 */

export interface User {
  /** Уникальный идентификатор пользователя */
  id: string;

  /** Email адрес пользователя */
  email: string;

  /** Имя пользователя */
  name?: string;

  /** Полное имя пользователя */
  fullName: string;

  /** Роль пользователя */
  role?: string;

  /** Разрешения пользователя */
  permissions?: string[];

  /** Дата последнего входа */
  last_login?: string;

  /** Дата создания аккаунта */
  created_at: string;

  /** Дата последнего обновления */
  updated_at: string;

  /** Статус активности аккаунта */
  is_active: boolean;
}

export interface AuthTokens {
  /** JWT токен доступа */
  access_token: string;

  /** JWT токен для обновления */
  refresh_token: string;

  /** Тип токена */
  token_type: string;

  /** Время жизни токена в секундах */
  expires_in: number;
}

export interface AuthResponse {
  /** Данные пользователя */
  user: User;

  /** Токены аутентификации */
  tokens: AuthTokens;
}


export interface AuthState {
  /** Данные текущего пользователя */
  user: User | null;

  /** Токены аутентификации */
  tokens: AuthTokens | null;

  /** Флаг аутентификации */
  isAuthenticated: boolean;

  /** Флаг загрузки */
  isLoading: boolean;

  /** Сообщение об ошибке */
  error: AuthError | null;
}

export interface AuthError {
  /** Тип ошибки */
  type: string;

  /** Сообщение об ошибке */
  message: string;

  /** Код ошибки */
  code?: string;

  /** Дополнительная информация об ошибке */
  details?: unknown;

  /** Временная метка ошибки */
  timestamp: string;
}



export interface LoginCredentials {
  /** Email пользователя */
  email: string;

  /** Пароль пользователя */
  password: string;
}

export interface RegisterData {
  /** Email пользователя */
  email: string;

  /** Пароль пользователя */
  password: string;

  /** Полное имя пользователя */
  full_name: string;
}

export interface ChangePasswordData {
  /** Текущий пароль */
  current_password: string;

  /** Новый пароль */
  new_password: string;
}

export interface ResetPasswordData {
  /** Email для сброса пароля */
  email: string;
}

export interface ResetPasswordConfirmData {
  /** Токен для подтверждения сброса */
  token: string;

  /** Новый пароль */
  new_password: string;
}

export interface LogoutData {
  /** Refresh token для инвалидации */
  refresh_token?: string;
}

/**
 * Конфигурация аутентификации
 */
export interface AuthConfig {
  /** Базовый URL API */
  apiBaseUrl?: string;
  /** Таймаут API запросов (мс) */
  apiTimeout?: number;
  /** Порог обновления токена (мс) */
  tokenRefreshThreshold?: number;
  /** Автоматическое обновление токенов */
  autoRefresh?: boolean;
  /** Редирект после входа */
  redirectAfterLogin?: string;
  /** Редирект после выхода */
  redirectAfterLogout?: string;
  /** Включить регистрацию */
  enableRegistration?: boolean;
  /** Включить сброс пароля */
  enablePasswordReset?: boolean;
  /** Включить социальный логин */
  enableSocialLogin?: boolean;
  /** Включить 2FA */
  enableTwoFactorAuth?: boolean;
  /** Включить HTTPS */
  enableHttps?: boolean;
  /** Включить CORS */
  corsEnabled?: boolean;
  /** Уровень логирования */
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
  /** TTL кеша (мс) */
  cacheTtl?: number;
  /** Язык по умолчанию */
  defaultLanguage?: string;
  /** Поддерживаемые языки */
  supportedLanguages?: string[];
  /** ID Google клиента */
  googleClientId?: string;
  /** ID Facebook app */
  facebookAppId?: string;
  /** ID GitHub клиента */
  githubClientId?: string;
  /** DSN Sentry */
  sentryDsn?: string;
  /** ID Google Analytics */
  googleAnalyticsId?: string;
  /** Макс размер файла (байт) */
  maxFileSize?: number;
  /** Разрешенные типы файлов */
  allowedFileTypes?: string[];
  /** Размер страницы по умолчанию */
  defaultPageSize?: number;
  /** Макс размер страницы */
  maxPageSize?: number;
  /** Включить Service Worker */
  enableServiceWorker?: boolean;
  /** Включить hot reload */
  enableHotReload?: boolean;
  /** Включить error boundary */
  enableErrorBoundary?: boolean;
  /** Включить мониторинг производительности */
  enablePerformanceMonitoring?: boolean;
  /** Включить devtools */
  enableDevtools?: boolean;
}

/**
 * Полная конфигурация аутентификации с обязательными полями
 */
export type AuthConfiguration = Required<AuthConfig>;