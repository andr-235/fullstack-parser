import { TestBed } from '@angular/core/testing';
import {
  Router,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
} from '@angular/router';
import { of } from 'rxjs';

import { AuthGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  const mockRoute = {} as ActivatedRouteSnapshot;
  const mockState = { url: '/protected' } as RouterStateSnapshot;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', [], {
      isAuthenticated$: of(true),
    });
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
      ],
    });

    guard = TestBed.inject(AuthGuard);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should allow access when user is authenticated', (done) => {
    authService.isAuthenticated$ = of(true);

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      expect(router.navigate).not.toHaveBeenCalled();
      done();
    });
  });

  it('should deny access and redirect when user is not authenticated', (done) => {
    authService.isAuthenticated$ = of(false);

    guard.canActivate(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/login'], {
        queryParams: { returnUrl: '/protected' },
      });
      done();
    });
  });

  it('should preserve return URL when redirecting', (done) => {
    authService.isAuthenticated$ = of(false);
    const stateWithUrl = { url: '/admin/settings' } as RouterStateSnapshot;

    guard.canActivate(mockRoute, stateWithUrl).subscribe((result) => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/login'], {
        queryParams: { returnUrl: '/admin/settings' },
      });
      done();
    });
  });

  it('should work with canActivateChild', (done) => {
    authService.isAuthenticated$ = of(true);

    guard.canActivateChild(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(true);
      done();
    });
  });

  it('should deny child access when not authenticated', (done) => {
    authService.isAuthenticated$ = of(false);

    guard.canActivateChild(mockRoute, mockState).subscribe((result) => {
      expect(result).toBe(false);
      expect(router.navigate).toHaveBeenCalledWith(['/login'], {
        queryParams: { returnUrl: '/protected' },
      });
      done();
    });
  });
});
