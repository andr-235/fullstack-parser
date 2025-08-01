import { Injectable } from '@angular/core';
import {
  HttpClient,
  HttpHeaders,
  HttpErrorResponse,
  HttpParams,
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, retry, tap, finalize } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { PerformanceService } from './performance.service';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
  timestamp?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = environment.apiUrl || 'http://localhost:3000/api';
  private loadingSubject = new BehaviorSubject<boolean>(false);
  public loading$ = this.loadingSubject.asObservable();

  constructor(
    private http: HttpClient,
    private performanceService: PerformanceService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = localStorage.getItem('auth_token');
    let headers = new HttpHeaders({
      'Content-Type': 'application/json',
    });

    if (token) {
      headers = headers.set('Authorization', `Bearer ${token}`);
    }

    return headers;
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred';
    let errorCode = 'UNKNOWN_ERROR';

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
      errorCode = 'CLIENT_ERROR';
    } else {
      // Server-side error
      errorCode = error.status.toString();
      switch (error.status) {
        case 400:
          errorMessage = 'Bad request - please check your input';
          break;
        case 401:
          errorMessage = 'Unauthorized - please log in again';
          // Redirect to login if unauthorized
          this.handleUnauthorized();
          break;
        case 403:
          errorMessage =
            "Forbidden - you don't have permission for this action";
          break;
        case 404:
          errorMessage = 'Resource not found';
          break;
        case 409:
          errorMessage = 'Conflict - the resource already exists';
          break;
        case 422:
          errorMessage = 'Validation error - please check your input';
          break;
        case 429:
          errorMessage = 'Too many requests - please try again later';
          break;
        case 500:
          errorMessage = 'Server error - please try again later';
          break;
        case 503:
          errorMessage = 'Service unavailable - please try again later';
          break;
        default:
          errorMessage = `Server error (${error.status})`;
      }
    }

    const apiError: ApiError = {
      message: errorMessage,
      code: errorCode,
      details: error.error,
    };

    return throwError(() => apiError);
  }

  private handleUnauthorized(): void {
    // Clear auth token and redirect to login
    localStorage.removeItem('auth_token');
    // You can inject Router here to navigate to login
    // this.router.navigate(['/login']);
  }

  private startLoading(): void {
    this.loadingSubject.next(true);
  }

  private stopLoading(): void {
    this.loadingSubject.next(false);
  }

  get<T>(endpoint: string, params?: any): Observable<T> {
    this.startLoading();
    const startTime = performance.now();
    const url = this.buildUrl(endpoint, params);

    return this.http.get<T>(url, { headers: this.getHeaders() }).pipe(
      tap(() => {
        const duration = performance.now() - startTime;
        this.performanceService.recordResponseTime(duration);
      }),
      catchError(this.handleError.bind(this)),
      finalize(() => this.stopLoading())
    );
  }

  private buildUrl(endpoint: string, params?: any): string {
    let url = `${this.baseUrl}${endpoint}`;

    if (params) {
      let httpParams = new HttpParams();
      Object.keys(params).forEach((key) => {
        if (params[key] !== undefined && params[key] !== null) {
          httpParams = httpParams.set(key, params[key].toString());
        }
      });
      const queryString = httpParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }

    return url;
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    this.startLoading();

    return this.http
      .post<T>(`${this.baseUrl}${endpoint}`, data, {
        headers: this.getHeaders(),
      })
      .pipe(
        retry(1),
        catchError(this.handleError.bind(this)),
        finalize(() => this.stopLoading())
      );
  }

  put<T>(endpoint: string, data: any): Observable<T> {
    this.startLoading();

    return this.http
      .put<T>(`${this.baseUrl}${endpoint}`, data, {
        headers: this.getHeaders(),
      })
      .pipe(
        retry(1),
        catchError(this.handleError.bind(this)),
        finalize(() => this.stopLoading())
      );
  }

  patch<T>(endpoint: string, data: any): Observable<T> {
    this.startLoading();

    return this.http
      .patch<T>(`${this.baseUrl}${endpoint}`, data, {
        headers: this.getHeaders(),
      })
      .pipe(
        retry(1),
        catchError(this.handleError.bind(this)),
        finalize(() => this.stopLoading())
      );
  }

  delete<T>(endpoint: string): Observable<T> {
    this.startLoading();

    return this.http
      .delete<T>(`${this.baseUrl}${endpoint}`, {
        headers: this.getHeaders(),
      })
      .pipe(
        retry(1),
        catchError(this.handleError.bind(this)),
        finalize(() => this.stopLoading())
      );
  }

  // Upload file method
  upload<T>(endpoint: string, file: File, additionalData?: any): Observable<T> {
    this.startLoading();

    const formData = new FormData();
    formData.append('file', file);

    if (additionalData) {
      Object.keys(additionalData).forEach((key) => {
        formData.append(key, additionalData[key]);
      });
    }

    const headers = new HttpHeaders();
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    return this.http
      .post<T>(`${this.baseUrl}${endpoint}`, formData, {
        headers,
      })
      .pipe(
        retry(1),
        catchError(this.handleError.bind(this)),
        finalize(() => this.stopLoading())
      );
  }

  // Download file method
  download(endpoint: string, filename?: string): Observable<Blob> {
    this.startLoading();

    return this.http
      .get(`${this.baseUrl}${endpoint}`, {
        headers: this.getHeaders(),
        responseType: 'blob',
      })
      .pipe(
        retry(1),
        catchError(this.handleError.bind(this)),
        finalize(() => this.stopLoading())
      );
  }

  // Health check method
  healthCheck(): Observable<{ status: string; timestamp: string }> {
    return this.http
      .get<{ status: string; timestamp: string }>(`${this.baseUrl}/health`, {
        headers: this.getHeaders(),
      })
      .pipe(retry(2), catchError(this.handleError.bind(this)));
  }
}
