import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AuthState } from '../app.state';
import * as fromAuth from './auth.reducer';

export const selectAuthState = createFeatureSelector<AuthState>('auth');

// User selectors
export const selectUser = createSelector(
  selectAuthState,
  (state) => state.user
);

export const selectIsAuthenticated = createSelector(
  selectAuthState,
  (state) => state.isAuthenticated
);

export const selectIsLoading = createSelector(
  selectAuthState,
  (state) => state.isLoading
);

export const selectError = createSelector(
  selectAuthState,
  (state) => state.error
);

export const selectToken = createSelector(
  selectAuthState,
  (state) => state.token
);

export const selectTokenExpiresAt = createSelector(
  selectAuthState,
  (state) => state.tokenExpiresAt
);

// Derived selectors
export const selectUserRole = createSelector(selectUser, (user) => user?.role);

export const selectUserUsername = createSelector(
  selectUser,
  (user) => user?.username
);

export const selectUserEmail = createSelector(
  selectUser,
  (user) => user?.email
);

export const selectIsAdmin = createSelector(
  selectUserRole,
  (role) => role === 'admin'
);

export const selectIsModerator = createSelector(
  selectUserRole,
  (role) => role === 'moderator'
);

export const selectIsUser = createSelector(
  selectUserRole,
  (role) => role === 'user'
);

export const selectHasRole = createSelector(
  selectUserRole,
  (role) => (requiredRole: string) => role === requiredRole
);

export const selectHasAnyRole = createSelector(
  selectUserRole,
  (role) => (requiredRoles: string[]) => requiredRoles.includes(role || '')
);

// Token selectors
export const selectIsTokenExpired = createSelector(
  selectTokenExpiresAt,
  (expiresAt) => {
    if (!expiresAt) return true;
    return new Date(expiresAt) <= new Date();
  }
);

export const selectIsTokenExpiringSoon = createSelector(
  selectTokenExpiresAt,
  (expiresAt) => {
    if (!expiresAt) return true;
    const expirationDate = new Date(expiresAt);
    const now = new Date();
    const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds
    return expirationDate.getTime() - now.getTime() < fiveMinutes;
  }
);

// Auth status selectors
export const selectAuthStatus = createSelector(
  selectIsAuthenticated,
  selectIsLoading,
  selectError,
  (isAuthenticated, isLoading, error) => ({
    isAuthenticated,
    isLoading,
    error,
  })
);

// Combined selectors for components
export const selectAuthData = createSelector(
  selectUser,
  selectIsAuthenticated,
  selectIsLoading,
  selectError,
  (user, isAuthenticated, isLoading, error) => ({
    user,
    isAuthenticated,
    isLoading,
    error,
  })
);
