import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

@Injectable({
  providedIn: 'root',
})
export class LoadingService {
  private loadingSubject = new BehaviorSubject<LoadingState>({
    isLoading: false,
    message: '',
    progress: 0,
  });

  public loading$ = this.loadingSubject.asObservable();

  constructor() {}

  show(message?: string): void {
    this.loadingSubject.next({
      isLoading: true,
      message: message || 'Loading...',
      progress: 0,
    });
  }

  hide(): void {
    this.loadingSubject.next({
      isLoading: false,
      message: '',
      progress: 0,
    });
  }

  updateProgress(progress: number, message?: string): void {
    const currentState = this.loadingSubject.value;
    this.loadingSubject.next({
      ...currentState,
      progress,
      message: message || currentState.message,
    });
  }

  updateMessage(message: string): void {
    const currentState = this.loadingSubject.value;
    this.loadingSubject.next({
      ...currentState,
      message,
    });
  }

  getCurrentState(): LoadingState {
    return this.loadingSubject.value;
  }

  // Convenience methods for common operations
  showWithMessage(message: string): void {
    this.show(message);
  }

  showProgress(message: string, progress: number): void {
    this.show(message);
    this.updateProgress(progress);
  }

  // Method to handle multiple concurrent operations
  private activeOperations = new Set<string>();

  startOperation(operationId: string, message?: string): void {
    this.activeOperations.add(operationId);
    this.show(message);
  }

  endOperation(operationId: string): void {
    this.activeOperations.delete(operationId);
    if (this.activeOperations.size === 0) {
      this.hide();
    }
  }

  isOperationActive(operationId: string): boolean {
    return this.activeOperations.has(operationId);
  }

  getActiveOperationsCount(): number {
    return this.activeOperations.size;
  }
}
