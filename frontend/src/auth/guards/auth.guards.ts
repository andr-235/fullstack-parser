import type { NavigationGuardNext, RouteLocationNormalized } from "vue-router";
import { useAuthStore } from "../stores/auth.store";
import type { User } from "../types";

/**
 * Интерфейс для конфигурации защиты роутов
 */
export interface RouteAuthMeta {
  requiresAuth?: boolean;
  requiresGuest?: boolean;
  requiredRoles?: string[];
  requiredPermissions?: string[];
}

/**
 * Интерфейс для контекста аутентификации в роутах
 */
export interface AuthContext {
  isAuthenticated: boolean;
  user: User | null;
  hasValidTokens: boolean;
  hasRole: (role: string) => boolean;
  hasPermission: (permission: string) => boolean;
}

/**
 * Создает контекст аутентификации для использования в guards
 */
export function createAuthContext(): AuthContext {
  const authStore = useAuthStore();

  return {
    isAuthenticated: authStore.isAuthenticated,
    user: authStore.user,
    hasValidTokens: authStore.hasValidTokens,
    hasRole: authStore.hasRole,
    hasPermission: authStore.hasPermission
  };
}

/**
 * Guard для проверки аутентификации пользователя
 * Перенаправляет неавторизованных пользователей на страницу входа
 */
export function requireAuth(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore();
  const authContext = createAuthContext();

  // Если роут требует аутентификации
  if (to.meta.requiresAuth) {
    // Проверяем, аутентифицирован ли пользователь
    if (!authContext.isAuthenticated) {
      // Сохраняем целевой роут для перенаправления после входа
      next({
        name: "login",
        query: { redirect: to.fullPath }
      });
      return;
    }

    // Проверяем валидность токенов
    if (!authContext.hasValidTokens) {
      // Попытка обновить токены
      authStore.refreshTokens()
        .then((success) => {
          if (!success) {
            // Если обновление не удалось, перенаправляем на вход
            next({
              name: "login",
              query: { redirect: to.fullPath }
            });
          } else {
            // Токены обновлены, продолжаем навигацию
            next();
          }
        })
        .catch(() => {
          next({
            name: "login",
            query: { redirect: to.fullPath }
          });
        });
      return;
    }

    // Проверяем роли, если они указаны
    const rolesMeta = to.meta as RouteAuthMeta;
    if (rolesMeta.requiredRoles && rolesMeta.requiredRoles.length > 0) {
      const hasRequiredRole = rolesMeta.requiredRoles.some((role: string) =>
        authContext.hasRole(role)
      );
  
      if (!hasRequiredRole) {
        next({ name: "unauthorized" });
        return;
      }
    }
  
    // Проверяем разрешения, если они указаны
    const permissionsMeta = to.meta as RouteAuthMeta;
    if (permissionsMeta.requiredPermissions && permissionsMeta.requiredPermissions.length > 0) {
      const hasRequiredPermission = permissionsMeta.requiredPermissions.some((permission: string) =>
        authContext.hasPermission(permission)
      );
  
      if (!hasRequiredPermission) {
        next({ name: "unauthorized" });
        return;
      }
    }

    // Все проверки пройдены, продолжаем навигацию
    next();
  } else {
    // Роут не требует аутентификации, продолжаем
    next();
  }
}

/**
 * Guard для проверки гостевого статуса
 * Перенаправляет аутентифицированных пользователей с гостевых страниц
 */
export function requireGuest(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authContext = createAuthContext();

  // Если роут требует гостевого статуса
  if (to.meta.requiresGuest) {
    if (authContext.isAuthenticated) {
      // Пользователь уже аутентифицирован, перенаправляем на главную
      next({ name: "home" });
    } else {
      // Пользователь не аутентифицирован, продолжаем
      next();
    }
  } else {
    // Роут не требует гостевого статуса, продолжаем
    next();
  }
}

/**
 * Комбинированный guard для аутентификации и гостевого статуса
 * Автоматически выбирает нужный guard на основе мета-данных роута
 */
export function authGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  console.log('authGuard: path=', to.path, 'isInitialized=', useAuthStore().isInitialized, 'requiresGuest=', to.meta.requiresGuest);
  const authContext = createAuthContext();

  // Для guest роутов не ждем инициализации store
  if (to.meta.requiresGuest) {
    requireGuest(to, from, next);
    return;
  }

  // Если пользователь не инициализирован, ждем инициализации
  if (!authContext.isAuthenticated && !useAuthStore().isInitialized) {
    // Ждем инициализации аутентификации
    const unwatch = useAuthStore().$subscribe(() => {
      if (useAuthStore().isInitialized) {
        unwatch();
        authGuard(to, from, next);
      }
    });
    return;
  }

  // Применяем соответствующий guard
  if (to.meta.requiresAuth) {
    requireAuth(to, from, next);
  } else {
    next();
  }
}

/**
 * Guard для проверки прав доступа на основе ролей и разрешений
 */
export function permissionGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authContext = createAuthContext();

  // Проверяем роли
  const roleMeta = to.meta as RouteAuthMeta;
  if (roleMeta.requiredRoles && roleMeta.requiredRoles.length > 0) {
    const hasRequiredRole = roleMeta.requiredRoles.some((role: string) =>
      authContext.hasRole(role)
    );

    if (!hasRequiredRole) {
      next({
        name: "unauthorized",
        query: { reason: "insufficient_role" }
      });
      return;
    }
  }

  // Проверяем разрешения
  const permMeta = to.meta as RouteAuthMeta;
  if (permMeta.requiredPermissions && permMeta.requiredPermissions.length > 0) {
    const hasRequiredPermission = permMeta.requiredPermissions.some((permission: string) =>
      authContext.hasPermission(permission)
    );

    if (!hasRequiredPermission) {
      next({
        name: "unauthorized",
        query: { reason: "insufficient_permission" }
      });
      return;
    }
  }

  next();
}

/**
 * Guard для проверки токенов и их обновления
 */
export function tokenGuard(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
): void {
  const authStore = useAuthStore();
  const authContext = createAuthContext();

  // Если пользователь аутентифицирован, проверяем токены
  if (authContext.isAuthenticated) {
    if (!authContext.hasValidTokens) {
      // Попытка обновить токены
      authStore.refreshTokens()
        .then((success) => {
          if (success) {
            next();
          } else {
            // Обновление не удалось, перенаправляем на вход
            next({
              name: "login",
              query: { redirect: to.fullPath }
            });
          }
        })
        .catch(() => {
          next({
            name: "login",
            query: { redirect: to.fullPath }
          });
        });
    } else {
      next();
    }
  } else {
    next();
  }
}

/**
 * Хелпер функция для создания защищенных роутов
 */
export function createProtectedRoute(
  path: string,
  component: any,
  meta: RouteAuthMeta = {}
) {
  return {
    path,
    component,
    meta: {
      requiresAuth: true,
      ...meta
    }
  };
}

/**
 * Хелпер функция для создания гостевых роутов
 */
export function createGuestRoute(
  path: string,
  component: any,
  meta: RouteAuthMeta = {}
) {
  return {
    path,
    component,
    meta: {
      requiresGuest: true,
      ...meta
    }
  };
}

/**
 * Хелпер функция для создания роутов с проверкой разрешений
 */
export function createPermissionRoute(
  path: string,
  component: any,
  requiredRoles: string[] = [],
  requiredPermissions: string[] = []
) {
  return {
    path,
    component,
    meta: {
      requiresAuth: true,
      requiredRoles,
      requiredPermissions
    }
  };
}