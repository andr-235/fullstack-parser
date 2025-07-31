import { TestBed } from '@angular/core/testing';
import {
  Router,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
} from '@angular/router';
import { of } from 'rxjs';

import { RoleGuard } from './role.guard';
import { AuthService } from '../services/auth.service';

describe('RoleGuard', () => {
  let guard: RoleGuard;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  const mockState = { url: '/admin' } as RouterStateSnapshot;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['hasAnyRole'], {
      currentUser$: of({ id: 1, username: 'testuser', role: 'user' }),
    });
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        RoleGuard,
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
      ],
    });

    guard = TestBed.inject(RoleGuard);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should allow access when user has required role', (done) => {
    const mockRoute = { data: { roles: ['user', 'admin'] } } as any;

    authService.hasAnyRole.and.returnValue(true);

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['user', 'admin']);
      expect(router.navigate).not.toHaveBeenCalled();
      done();
    });
  });

  it('should deny access when user does not have required role', (done) => {
    const mockRoute = { data: { roles: ['admin'] } } as any;

    authService.hasAnyRole.and.returnValue(false);

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(false);
      expect(authService.hasAnyRole).toHaveBeenCalledWith(['admin']);
      expect(router.navigate).toHaveBeenCalledWith(['/access-denied']);
      done();
    });
  });

  it('should allow access when no roles are specified', (done) => {
    const mockRoute = { data: {} } as any;

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      expect(authService.hasAnyRole).not.toHaveBeenCalled();
      done();
    });
  });

  it('should redirect to login when user is not authenticated', (done) => {
    const mockRoute = { data: { roles: ['admin'] } } as any;

    authService.currentUser$ = of(null);

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/login'], {
        queryParams: { returnUrl: '/admin' },
      });
      done();
    });
  });

  it('should handle empty roles array', (done) => {
    const mockRoute = { data: { roles: [] } } as any;

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      expect(authService.hasAnyRole).not.toHaveBeenCalled();
      done();
    });
  });

  it('should handle null roles', (done) => {
    const mockRoute = { data: { roles: null } } as any;

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      expect(authService.hasAnyRole).not.toHaveBeenCalled();
      done();
    });
  });

  it('should handle undefined roles', (done) => {
    const mockRoute = { data: { roles: undefined } } as any;

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      expect(authService.hasAnyRole).not.toHaveBeenCalled();
      done();
    });
  });
});
