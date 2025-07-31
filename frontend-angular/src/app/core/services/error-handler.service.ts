import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiError } from './api.service';

export interface ErrorNotification {
  message: string;
  type: 'error' | 'warning' | 'info';
  duration?: number;
  action?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ErrorHandlerService {
  private errorLog: ApiError[] = [];

  constructor(private snackBar: MatSnackBar) {}

  handleError(error: ApiError, showNotification: boolean = true): void {
    // Log the error
    this.errorLog.push({
      ...error,
      timestamp: new Date().toISOString(),
    });

    // Show notification if requested
    if (showNotification) {
      this.showErrorNotification(error.message);
    }

    // Log to console for debugging
    console.error('API Error:', error);

    // In production, you might want to send errors to a logging service
    // this.sendToLoggingService(error);
  }

  showErrorNotification(message: string, duration: number = 5000): void {
    this.snackBar.open(message, 'Close', {
      duration,
      panelClass: ['error-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  showWarningNotification(message: string, duration: number = 4000): void {
    this.snackBar.open(message, 'Close', {
      duration,
      panelClass: ['warning-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  showInfoNotification(message: string, duration: number = 3000): void {
    this.snackBar.open(message, 'Close', {
      duration,
      panelClass: ['info-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  showSuccessNotification(message: string, duration: number = 3000): void {
    this.snackBar.open(message, 'Close', {
      duration,
      panelClass: ['success-snackbar'],
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
    });
  }

  getErrorLog(): ApiError[] {
    return [...this.errorLog];
  }

  clearErrorLog(): void {
    this.errorLog = [];
  }

  getRecentErrors(count: number = 10): ApiError[] {
    return this.errorLog.slice(-count);
  }

  getErrorsByCode(code: string): ApiError[] {
    return this.errorLog.filter((error) => error.code === code);
  }

  // Handle specific error types
  handleNetworkError(): void {
    this.showErrorNotification('Network error - please check your connection');
  }

  handleValidationError(errors: any): void {
    const message = this.formatValidationErrors(errors);
    this.showErrorNotification(message);
  }

  handleServerError(): void {
    this.showErrorNotification('Server error - please try again later');
  }

  handleUnauthorizedError(): void {
    this.showWarningNotification('Session expired - please log in again');
  }

  handleForbiddenError(): void {
    this.showErrorNotification(
      "Access denied - you don't have permission for this action"
    );
  }

  private formatValidationErrors(errors: any): string {
    if (typeof errors === 'string') {
      return errors;
    }

    if (Array.isArray(errors)) {
      return errors.join(', ');
    }

    if (typeof errors === 'object') {
      const errorMessages = Object.values(errors).flat();
      return errorMessages.join(', ');
    }

    return 'Validation error occurred';
  }

  // Method to send errors to external logging service
  private sendToLoggingService(error: ApiError): void {
    // Implementation for sending errors to external service
    // Example: Sentry, LogRocket, etc.
    console.log('Sending error to logging service:', error);
  }
}
