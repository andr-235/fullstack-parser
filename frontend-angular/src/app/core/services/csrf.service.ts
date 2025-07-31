import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class CsrfService {
  private readonly CSRF_TOKEN_KEY = 'csrf_token';
  private readonly CSRF_TOKEN_EXPIRY_KEY = 'csrf_token_expiry';

  constructor(private http: HttpClient) {}

  /**
   * Get CSRF token from server
   */
  getCsrfToken(): Observable<string> {
    return this.http.get<{ token: string }>('/api/csrf-token').pipe(
      tap((response) => {
        this.storeCsrfToken(response.token);
      }),
      map((response) => response.token),
      catchError((error) => {
        console.error('Failed to get CSRF token:', error);
        return of('');
      })
    );
  }

  /**
   * Get stored CSRF token
   */
  getStoredCsrfToken(): string | null {
    const token = localStorage.getItem(this.CSRF_TOKEN_KEY);
    const expiry = localStorage.getItem(this.CSRF_TOKEN_EXPIRY_KEY);

    if (token && expiry) {
      const expiryDate = new Date(expiry);
      if (expiryDate > new Date()) {
        return token;
      } else {
        // Token expired, remove it
        this.clearCsrfToken();
      }
    }

    return null;
  }

  /**
   * Store CSRF token with expiry
   */
  private storeCsrfToken(token: string): void {
    const expiry = new Date();
    expiry.setHours(expiry.getHours() + 1); // Token expires in 1 hour

    localStorage.setItem(this.CSRF_TOKEN_KEY, token);
    localStorage.setItem(this.CSRF_TOKEN_EXPIRY_KEY, expiry.toISOString());
  }

  /**
   * Clear stored CSRF token
   */
  clearCsrfToken(): void {
    localStorage.removeItem(this.CSRF_TOKEN_KEY);
    localStorage.removeItem(this.CSRF_TOKEN_EXPIRY_KEY);
  }

  /**
   * Refresh CSRF token
   */
  refreshCsrfToken(): Observable<string> {
    this.clearCsrfToken();
    return this.getCsrfToken();
  }

  /**
   * Check if CSRF token is valid
   */
  isCsrfTokenValid(): boolean {
    const token = this.getStoredCsrfToken();
    return token !== null && token.length > 0;
  }

  /**
   * Get CSRF token for headers
   */
  getCsrfTokenForHeaders(): string | null {
    return this.getStoredCsrfToken();
  }

  /**
   * Initialize CSRF protection
   */
  initializeCsrfProtection(): Observable<string> {
    if (this.isCsrfTokenValid()) {
      return of(this.getStoredCsrfToken()!);
    } else {
      return this.getCsrfToken();
    }
  }
}
