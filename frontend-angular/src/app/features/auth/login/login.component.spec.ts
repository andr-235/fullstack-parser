import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { provideMockStore, MockStore } from '@ngrx/store/testing';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { LoginComponent } from './login.component';
import { AuthService } from '../../../core/services/auth.service';
import { ErrorHandlerService } from '../../../core/services/error-handler.service';
import { LoadingService } from '../../../core/services/loading.service';
import * as AuthSelectors from '../../../core/store/auth/auth.selectors';

describe('LoginComponent with NgRx', () => {
  let component: LoginComponent;
  let fixture: ComponentFixture<LoginComponent>;
  let store: MockStore<any>;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;
  let errorHandler: jasmine.SpyObj<ErrorHandlerService>;
  let loadingService: jasmine.SpyObj<LoadingService>;

  beforeEach(async () => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', [
      'login',
      'isAuthenticated',
      'getCurrentUser',
    ]);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);
    const errorHandlerSpy = jasmine.createSpyObj('ErrorHandlerService', [
      'handleError',
      'showSuccessNotification',
    ]);
    const loadingServiceSpy = jasmine.createSpyObj('LoadingService', [
      'show',
      'hide',
    ]);

    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatCheckboxModule,
        MatDividerModule,
        MatSnackBarModule,
        MatProgressSpinnerModule,
        BrowserAnimationsModule,
      ],
      declarations: [LoginComponent],
      providers: [
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy },
        { provide: ErrorHandlerService, useValue: errorHandlerSpy },
        { provide: LoadingService, useValue: loadingServiceSpy },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              queryParams: {},
            },
          },
        },
        provideMockStore({
          initialState: {},
          selectors: [
            { selector: AuthSelectors.selectIsLoading, value: false },
            { selector: AuthSelectors.selectError, value: null },
            { selector: AuthSelectors.selectIsAuthenticated, value: false },
          ],
        }),
      ],
    }).compileComponents();

    store = TestBed.inject(MockStore);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    errorHandler = TestBed.inject(
      ErrorHandlerService
    ) as jasmine.SpyObj<ErrorHandlerService>;
    loadingService = TestBed.inject(
      LoadingService
    ) as jasmine.SpyObj<LoadingService>;
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with store observables', () => {
    expect(component.isLoading$).toBeDefined();
    expect(component.error$).toBeDefined();
  });

  it('should dispatch login action when form is submitted', () => {
    spyOn(store, 'dispatch');

    component.loginForm.patchValue({
      username: 'testuser',
      password: 'testpass',
    });

    component.onSubmit();

    expect(store.dispatch).toHaveBeenCalled();
  });

  it('should not dispatch action when form is invalid', () => {
    spyOn(store, 'dispatch');

    component.loginForm.patchValue({
      username: '',
      password: '',
    });

    component.onSubmit();

    expect(store.dispatch).not.toHaveBeenCalled();
  });

  it('should clean up subscriptions on destroy', () => {
    spyOn(component['destroy$'], 'next');
    spyOn(component['destroy$'], 'complete');

    component.ngOnDestroy();

    expect(component['destroy$'].next).toHaveBeenCalled();
    expect(component['destroy$'].complete).toHaveBeenCalled();
  });
});
