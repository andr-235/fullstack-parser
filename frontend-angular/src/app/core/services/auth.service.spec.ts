import { TestBed } from '@angular/core/testing';
import {
  HttpClientTestingModule,
  HttpTestingController,
} from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { of, throwError } from 'rxjs';

import {
  AuthService,
  LoginCredentials,
  RegisterRequest,
  User,
} from './auth.service';
import { ErrorHandlerService } from './error-handler.service';
import { LoadingService } from './loading.service';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let router: jasmine.SpyObj<Router>;
  let errorHandler: jasmine.SpyObj<ErrorHandlerService>;
  let loadingService: jasmine.SpyObj<LoadingService>;

  const mockUser: User = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    role: 'user',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
  };

  const mockAuthResponse = {
    user: mockUser,
    token: 'mock-jwt-token',
    expires_at: '2024-12-31T23:59:59Z',
  };

  beforeEach(() => {
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const errorHandlerSpy = jasmine.createSpyObj('ErrorHandlerService', [
      'handleError',
      'showSuccessNotification',
    ]);
    const loadingServiceSpy = jasmine.createSpyObj('LoadingService', [
      'show',
      'hide',
    ]);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        AuthService,
        { provide: Router, useValue: routerSpy },
        { provide: ErrorHandlerService, useValue: errorHandlerSpy },
        { provide: LoadingService, useValue: loadingServiceSpy },
      ],
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    errorHandler = TestBed.inject(
      ErrorHandlerService
    ) as jasmine.SpyObj<ErrorHandlerService>;
    loadingService = TestBed.inject(
      LoadingService
    ) as jasmine.SpyObj<LoadingService>;
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    const credentials: LoginCredentials = {
      username: 'testuser',
      password: 'testpass',
    };

    it('should login successfully', () => {
      service.login(credentials).subscribe((response) => {
        expect(response).toEqual(mockAuthResponse);
        expect(service.getCurrentUser()).toEqual(mockUser);
        expect(service.isAuthenticated()).toBe(true);
      });

      const req = httpMock.expectOne('/auth/login');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(credentials);
      req.flush(mockAuthResponse);

      expect(loadingService.show).toHaveBeenCalledWith('Вход в систему...');
      expect(loadingService.hide).toHaveBeenCalled();
      expect(errorHandler.showSuccessNotification).toHaveBeenCalledWith(
        'Успешный вход в систему'
      );
      expect(router.navigate).toHaveBeenCalledWith(['/dashboard']);
    });

    it('should handle login error', () => {
      const errorMessage = 'Invalid credentials';

      service.login(credentials).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/auth/login');
      req.flush(
        { message: errorMessage },
        { status: 401, statusText: 'Unauthorized' }
      );

      expect(loadingService.hide).toHaveBeenCalled();
      expect(errorHandler.handleError).toHaveBeenCalled();
    });
  });

  describe('logout', () => {
    it('should logout successfully', () => {
      // Setup authenticated state
      localStorage.setItem('auth_token', 'mock-token');
      localStorage.setItem('auth_expires', '2024-12-31T23:59:59Z');

      service.logout().subscribe(() => {
        expect(service.getCurrentUser()).toBeNull();
        expect(service.isAuthenticated()).toBe(false);
        expect(localStorage.getItem('auth_token')).toBeNull();
        expect(localStorage.getItem('auth_expires')).toBeNull();
      });

      const req = httpMock.expectOne('/auth/logout');
      expect(req.request.method).toBe('POST');
      req.flush({});

      expect(loadingService.show).toHaveBeenCalledWith('Выход из системы...');
      expect(loadingService.hide).toHaveBeenCalled();
      expect(errorHandler.showSuccessNotification).toHaveBeenCalledWith(
        'Успешный выход из системы'
      );
      expect(router.navigate).toHaveBeenCalledWith(['/login']);
    });

    it('should handle logout error but still clear local state', () => {
      // Setup authenticated state
      localStorage.setItem('auth_token', 'mock-token');

      service.logout().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe('Network error');
        },
      });

      const req = httpMock.expectOne('/auth/logout');
      req.error(new ErrorEvent('Network error'));

      // Should still clear local state even on error
      expect(service.getCurrentUser()).toBeNull();
      expect(service.isAuthenticated()).toBe(false);
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('register', () => {
    const registerRequest: RegisterRequest = {
      username: 'newuser',
      password: 'newpass',
    };

    it('should register successfully', () => {
      service.register(registerRequest).subscribe((response) => {
        expect(response).toEqual(mockAuthResponse);
        expect(service.getCurrentUser()).toEqual(mockUser);
        expect(service.isAuthenticated()).toBe(true);
      });

      const req = httpMock.expectOne('/auth/register');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(registerRequest);
      req.flush(mockAuthResponse);

      expect(loadingService.show).toHaveBeenCalledWith('Регистрация...');
      expect(loadingService.hide).toHaveBeenCalled();
      expect(errorHandler.showSuccessNotification).toHaveBeenCalledWith(
        'Регистрация успешна'
      );
    });

    it('should handle registration error', () => {
      const errorMessage = 'Username already exists';

      service.register(registerRequest).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe(errorMessage);
        },
      });

      const req = httpMock.expectOne('/auth/register');
      req.flush(
        { message: errorMessage },
        { status: 400, statusText: 'Bad Request' }
      );

      expect(loadingService.hide).toHaveBeenCalled();
      expect(errorHandler.handleError).toHaveBeenCalled();
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', () => {
      service.refreshToken().subscribe((response) => {
        expect(response).toEqual(mockAuthResponse);
      });

      const req = httpMock.expectOne('/auth/refresh');
      expect(req.request.method).toBe('POST');
      req.flush(mockAuthResponse);
    });

    it('should handle refresh token error', () => {
      service.refreshToken().subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toBe('Token expired');
        },
      });

      const req = httpMock.expectOne('/auth/refresh');
      req.flush(
        { message: 'Token expired' },
        { status: 401, statusText: 'Unauthorized' }
      );

      // Should logout on refresh failure
      expect(service.getCurrentUser()).toBeNull();
      expect(service.isAuthenticated()).toBe(false);
    });
  });

  describe('role checking', () => {
    beforeEach(() => {
      // Setup authenticated user
      service['currentUserSubject'].next(mockUser);
      service['isAuthenticatedSubject'].next(true);
    });

    it('should check user role correctly', () => {
      expect(service.hasRole('user')).toBe(true);
      expect(service.hasRole('admin')).toBe(false);
    });

    it('should check multiple roles correctly', () => {
      expect(service.hasAnyRole(['user', 'admin'])).toBe(true);
      expect(service.hasAnyRole(['admin', 'moderator'])).toBe(false);
    });
  });

  describe('token expiration', () => {
    it('should detect expiring token', () => {
      const futureDate = new Date();
      futureDate.setMinutes(futureDate.getMinutes() + 3); // 3 minutes from now

      localStorage.setItem('auth_expires', futureDate.toISOString());

      expect(service.isTokenExpiringSoon()).toBe(true);
    });

    it('should not detect expiring token when far from expiration', () => {
      const futureDate = new Date();
      futureDate.setHours(futureDate.getHours() + 2); // 2 hours from now

      localStorage.setItem('auth_expires', futureDate.toISOString());

      expect(service.isTokenExpiringSoon()).toBe(false);
    });
  });

  describe('checkAuthStatus', () => {
    it('should load user if valid token exists', () => {
      localStorage.setItem('auth_token', 'valid-token');
      localStorage.setItem('auth_expires', '2024-12-31T23:59:59Z');

      service['checkAuthStatus']();

      const req = httpMock.expectOne('/auth/me');
      req.flush(mockUser);

      expect(service.getCurrentUser()).toEqual(mockUser);
      expect(service.isAuthenticated()).toBe(true);
    });

    it('should logout if token is expired', () => {
      const pastDate = new Date();
      pastDate.setHours(pastDate.getHours() - 1); // 1 hour ago

      localStorage.setItem('auth_token', 'expired-token');
      localStorage.setItem('auth_expires', pastDate.toISOString());

      service['checkAuthStatus']();

      expect(service.getCurrentUser()).toBeNull();
      expect(service.isAuthenticated()).toBe(false);
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });
});
