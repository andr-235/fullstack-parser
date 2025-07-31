import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject, throwError } from 'rxjs';
import { tap, catchError } from 'rxjs/operators';
import { ApiService, ApiError } from './api.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';
import { Router } from '@angular/router';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  role: 'admin' | 'user' | 'moderator';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  expires_at: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  private isAuthenticatedSubject = new BehaviorSubject<boolean>(false);
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private apiService: ApiService,
    private errorHandler: ErrorHandlerService,
    private loadingService: LoadingService,
    private router: Router
  ) {
    this.checkAuthStatus();
  }

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    this.loadingService.show('Вход в систему...');

    return this.apiService.post<AuthResponse>('/auth/login', credentials).pipe(
      tap((response) => {
        this.loadingService.hide();
        this.handleSuccessfulAuth(response);
        this.errorHandler.showSuccessNotification('Успешный вход в систему');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  logout(): Observable<void> {
    this.loadingService.show('Выход из системы...');

    return this.apiService.post<void>('/auth/logout', {}).pipe(
      tap(() => {
        this.loadingService.hide();
        this.handleLogout();
        this.errorHandler.showSuccessNotification('Успешный выход из системы');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.handleLogout(); // Logout locally even if server request fails
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  register(request: RegisterRequest): Observable<AuthResponse> {
    this.loadingService.show('Регистрация...');

    return this.apiService.post<AuthResponse>('/auth/register', request).pipe(
      tap((response) => {
        this.loadingService.hide();
        this.handleSuccessfulAuth(response);
        this.errorHandler.showSuccessNotification('Регистрация успешна');
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  refreshToken(): Observable<AuthResponse> {
    return this.apiService.post<AuthResponse>('/auth/refresh', {}).pipe(
      tap((response) => {
        this.handleSuccessfulAuth(response);
      }),
      catchError((error: ApiError) => {
        this.handleLogout();
        throw error;
      })
    );
  }

  changePassword(
    currentPassword: string,
    newPassword: string
  ): Observable<void> {
    this.loadingService.show('Изменение пароля...');

    return this.apiService
      .post<void>('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification('Пароль успешно изменен');
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  forgotPassword(email: string): Observable<void> {
    this.loadingService.show('Отправка инструкций...');

    return this.apiService.post<void>('/auth/forgot-password', { email }).pipe(
      tap(() => {
        this.loadingService.hide();
        this.errorHandler.showSuccessNotification(
          'Инструкции отправлены на ваш email'
        );
      }),
      catchError((error: ApiError) => {
        this.loadingService.hide();
        this.errorHandler.handleError(error);
        throw error;
      })
    );
  }

  resetPassword(token: string, newPassword: string): Observable<void> {
    this.loadingService.show('Сброс пароля...');

    return this.apiService
      .post<void>('/auth/reset-password', {
        token,
        new_password: newPassword,
      })
      .pipe(
        tap(() => {
          this.loadingService.hide();
          this.errorHandler.showSuccessNotification('Пароль успешно сброшен');
        }),
        catchError((error: ApiError) => {
          this.loadingService.hide();
          this.errorHandler.handleError(error);
          throw error;
        })
      );
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return this.isAuthenticatedSubject.value;
  }

  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user ? user.role === role : false;
  }

  hasAnyRole(roles: string[]): boolean {
    const user = this.getCurrentUser();
    return user ? roles.includes(user.role) : false;
  }

  private handleSuccessfulAuth(response: AuthResponse): void {
    // Store token
    localStorage.setItem('auth_token', response.token);
    localStorage.setItem('auth_expires', response.expires_at);

    // Update user state
    this.currentUserSubject.next(response.user);
    this.isAuthenticatedSubject.next(true);

    // Navigate to dashboard
    this.router.navigate(['/dashboard']);
  }

  private handleLogout(): void {
    // Clear stored data
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_expires');

    // Update state
    this.currentUserSubject.next(null);
    this.isAuthenticatedSubject.next(false);

    // Navigate to login
    this.router.navigate(['/login']);
  }

  private checkAuthStatus(): void {
    const token = localStorage.getItem('auth_token');
    const expiresAt = localStorage.getItem('auth_expires');

    if (token && expiresAt) {
      const expirationDate = new Date(expiresAt);
      const now = new Date();

      if (expirationDate > now) {
        // Token is still valid, try to get user info
        this.getUserInfo().subscribe({
          next: (user) => {
            this.currentUserSubject.next(user);
            this.isAuthenticatedSubject.next(true);
          },
          error: () => {
            this.handleLogout();
          },
        });
      } else {
        // Token expired
        this.handleLogout();
      }
    }
  }

  private getUserInfo(): Observable<User> {
    return this.apiService.get<User>('/auth/me');
  }

  // Check if token is about to expire (within 5 minutes)
  isTokenExpiringSoon(): boolean {
    const expiresAt = localStorage.getItem('auth_expires');
    if (!expiresAt) return true;

    const expirationDate = new Date(expiresAt);
    const now = new Date();
    const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds

    return expirationDate.getTime() - now.getTime() < fiveMinutes;
  }

  // Auto-refresh token if needed
  autoRefreshToken(): void {
    if (this.isTokenExpiringSoon() && this.isAuthenticated()) {
      this.refreshToken().subscribe({
        error: () => {
          this.handleLogout();
        },
      });
    }
  }
}
