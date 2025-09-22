import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { User, AuthTokens, AuthError, AuthResponse } from "../types";
// Константы типов ошибок
const AUTH_ERROR_TYPES = {
  INITIALIZATION_ERROR: 'INITIALIZATION_ERROR',
  LOGIN_ERROR: 'LOGIN_ERROR',
  REGISTRATION_ERROR: 'REGISTRATION_ERROR',
  TOKEN_REFRESH_ERROR: 'TOKEN_REFRESH_ERROR',
  PASSWORD_CHANGE_ERROR: 'PASSWORD_CHANGE_ERROR',
  PASSWORD_RESET_ERROR: 'PASSWORD_RESET_ERROR'
} as const;
import { AuthService } from "../services/auth.service";

/**
 * Хранилище состояния аутентификации
 * Управляет данными пользователя, токенами и состоянием аутентификации
 */
export const useAuthStore = defineStore("auth", () => {
  // Состояние
  const user = ref<User | null>(null);
  const tokens = ref<AuthTokens | null>(null);
  const isLoading = ref<boolean>(false);
  const error = ref<AuthError | null>(null);
  const isInitialized = ref<boolean>(false);

  // Геттеры
  const isAuthenticated = computed<boolean>(() => {
    return !!(user.value && tokens.value?.access_token);
  });

  const hasValidTokens = computed<boolean>(() => {
    if (!tokens.value) return false;

    try {
      // Проверяем, не истек ли токен
      const tokenPayload = JSON.parse(atob(tokens.value.access_token.split(".")[1]));
      const currentTime = Date.now() / 1000;

      return tokenPayload.exp > currentTime;
    } catch {
      return false;
    }
  });

  const userRole = computed<string | null>(() => {
    return user.value?.role || null;
  });

  const userPermissions = computed<string[]>(() => {
    return user.value?.permissions || [];
  });

  // Действия
  const setLoading = (loading: boolean): void => {
    isLoading.value = loading;
  };

  const setError = (authError: AuthError | null): void => {
    error.value = authError;
  };

  const clearError = (): void => {
    error.value = null;
  };

  const setUser = (userData: User | null): void => {
    user.value = userData;
  };

  const setTokens = (tokenData: AuthTokens | null): void => {
    tokens.value = tokenData;

    // Сохраняем токены в localStorage для персистентности
    if (tokenData) {
      localStorage.setItem("auth_tokens", JSON.stringify(tokenData));
    } else {
      localStorage.removeItem("auth_tokens");
    }
  };

  const initializeAuth = async (): Promise<void> => {
    if (isInitialized.value) return;

    try {
      setLoading(true);
      clearError();

      // Проверяем сохраненные токены
      const savedTokens = localStorage.getItem("auth_tokens");

      if (savedTokens) {
        const parsedTokens: AuthTokens = JSON.parse(savedTokens);

        // Проверяем валидность токенов
        if (parsedTokens.access_token) {
          try {
            // Получаем информацию о текущем пользователе
            const userData = await AuthService.getCurrentUser();
            if (userData) {
              setUser(userData);
            } else {
              setUser(null);
            }
            setTokens(parsedTokens);
          } catch (err) {
            // Токены недействительны, очищаем их
            localStorage.removeItem("auth_tokens");
            setUser(null);
            setTokens(null);
          }
        }
      }
    } catch (err) {
      console.error("Ошибка инициализации аутентификации:", err);
      setError({
        type: AUTH_ERROR_TYPES.INITIALIZATION_ERROR,
        message: "Не удалось инициализировать аутентификацию",
        code: "INIT_FAILED",
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
      isInitialized.value = true;
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      clearError();

      const response: AuthResponse = await AuthService.login({ email, password });

      setUser(response.user);
      setTokens(response.tokens);

      return true;
    } catch (err: any) {
      const authError: AuthError = {
        type: AUTH_ERROR_TYPES.LOGIN_ERROR,
        message: err.message || "Ошибка входа в систему",
        code: err.code || "LOGIN_FAILED",
        timestamp: new Date().toISOString()
      };

      setError(authError);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (
    email: string,
    password: string,
    fullName: string
  ): Promise<boolean> => {
    try {
      setLoading(true);
      clearError();

      const response: AuthResponse = await AuthService.register({ email, password, full_name: fullName });

      setUser(response.user);
      setTokens(response.tokens);

      return true;
    } catch (err: any) {
      const authError: AuthError = {
        type: AUTH_ERROR_TYPES.REGISTRATION_ERROR,
        message: err.message || "Ошибка регистрации",
        code: err.code || "REGISTRATION_FAILED",
        timestamp: new Date().toISOString()
      };

      setError(authError);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setLoading(true);

      // Вызываем API logout если есть refresh токен
      if (tokens.value?.refresh_token) {
        try {
          await AuthService.logout({ refresh_token: tokens.value.refresh_token });
        } catch (err) {
          // Игнорируем ошибки logout API, просто очищаем локальное состояние
          console.warn("Ошибка при вызове logout API:", err);
        }
      }

      // Очищаем состояние
      setUser(null);
      setTokens(null);
      clearError();
    } catch (err) {
      console.error("Ошибка при выходе из системы:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshTokens = async (): Promise<boolean> => {
    if (!tokens.value?.refresh_token) {
      return false;
    }

    try {
      setLoading(true);
      clearError();

      const response: AuthTokens = await AuthService.refreshToken({ refresh_token: tokens.value.refresh_token });

      setTokens({
        ...response,
        refresh_token: tokens.value.refresh_token // refresh токен остается тем же
      });

      return true;
    } catch (err: any) {
      // Если обновление токенов не удалось, выходим из системы
      await logout();

      const authError: AuthError = {
        type: AUTH_ERROR_TYPES.TOKEN_REFRESH_ERROR,
        message: "Сессия истекла. Пожалуйста, войдите снова.",
        code: "TOKEN_REFRESH_FAILED",
        timestamp: new Date().toISOString()
      };

      setError(authError);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (
    currentPassword: string,
    newPassword: string
  ): Promise<boolean> => {
    try {
      setLoading(true);
      clearError();

      await AuthService.changePassword({ current_password: currentPassword, new_password: newPassword });

      return true;
    } catch (err: any) {
      const authError: AuthError = {
        type: AUTH_ERROR_TYPES.PASSWORD_CHANGE_ERROR,
        message: err.message || "Ошибка смены пароля",
        code: err.code || "PASSWORD_CHANGE_FAILED",
        timestamp: new Date().toISOString()
      };

      setError(authError);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (email: string): Promise<boolean> => {
    try {
      setLoading(true);
      clearError();

      await AuthService.resetPassword({ email });

      return true;
    } catch (err: any) {
      const authError: AuthError = {
        type: AUTH_ERROR_TYPES.PASSWORD_RESET_ERROR,
        message: err.message || "Ошибка сброса пароля",
        code: err.code || "PASSWORD_RESET_FAILED",
        timestamp: new Date().toISOString()
      };

      setError(authError);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const updateUserProfile = (userData: Partial<User>): void => {
    if (user.value) {
      setUser({ ...user.value, ...userData });
    }
  };

  const hasPermission = (permission: string): boolean => {
    return userPermissions.value.includes(permission);
  };

  const hasRole = (role: string): boolean => {
    return userRole.value === role;
  };

  const getCurrentUser = async (): Promise<User | null> => {
    try {
      setLoading(true);
      clearError();

      const userData = await AuthService.getCurrentUser();
      if (userData) {
        setUser(userData);
        return userData;
      }
      return null;
    } catch (err: any) {
      const authError: AuthError = {
        type: AUTH_ERROR_TYPES.INITIALIZATION_ERROR,
        message: err.message || "Ошибка получения данных пользователя",
        code: "GET_USER_FAILED",
        timestamp: new Date().toISOString()
      };

      setError(authError);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    // Состояние
    user,
    tokens,
    isLoading,
    error,
    isInitialized,

    // Геттеры
    isAuthenticated,
    hasValidTokens,
    userRole,
    userPermissions,

    // Действия
    setLoading,
    setError,
    clearError,
    setUser,
    setTokens,
    initializeAuth,
    login,
    register,
    logout,
    refreshTokens,
    changePassword,
    resetPassword,
    updateUserProfile,
    hasPermission,
    hasRole,
    getCurrentUser
  };
});