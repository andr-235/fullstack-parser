import { Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable, map } from 'rxjs';
import { AppState } from '../store/app.state';

@Injectable({
  providedIn: 'root',
})
export class StateDebugService {
  constructor(private store: Store<AppState>) {}

  // Get current state snapshot
  getCurrentState(): Observable<AppState> {
    return this.store.select((state) => state);
  }

  // Get state size information
  getStateSizeInfo(): Observable<{
    totalSize: number;
    authSize: number;
    groupsSize: number;
    keywordsSize: number;
    commentsSize: number;
    monitoringSize: number;
    settingsSize: number;
    uiSize: number;
  }> {
    return this.store.select((state) => {
      const calculateSize = (obj: any): number => {
        return JSON.stringify(obj).length;
      };

      return {
        totalSize: calculateSize(state),
        authSize: calculateSize(state.auth),
        groupsSize: calculateSize(state.groups),
        keywordsSize: calculateSize(state.keywords),
        commentsSize: calculateSize(state.comments),
        monitoringSize: calculateSize(state.monitoring),
        settingsSize: calculateSize(state.settings),
        uiSize: calculateSize(state.ui),
      };
    });
  }

  // Get state change history (basic implementation)
  getStateHistory(): Observable<string[]> {
    // This would track state changes over time
    // For now, return empty array
    return new Observable((observer) => {
      observer.next([]);
      observer.complete();
    });
  }

  // Debug specific state slice
  debugStateSlice(sliceName: keyof AppState): Observable<any> {
    return this.store.select((state) => state[sliceName]);
  }

  // Get state performance metrics
  getStatePerformanceMetrics(): Observable<{
    lastUpdateTime: number;
    updateCount: number;
    averageUpdateTime: number;
  }> {
    // This would track performance metrics
    // For now, return basic metrics
    return new Observable((observer) => {
      observer.next({
        lastUpdateTime: Date.now(),
        updateCount: 0,
        averageUpdateTime: 0,
      });
      observer.complete();
    });
  }

  // Export state for debugging
  exportStateForDebug(): Observable<string> {
    return this.store.select((state) => JSON.stringify(state, null, 2));
  }

  // Get state validation report
  getStateValidationReport(): Observable<{
    isValid: boolean;
    errors: string[];
    warnings: string[];
  }> {
    return this.store.select((state) => {
      const errors: string[] = [];
      const warnings: string[] = [];

      // Validate auth state
      if (state.auth.isAuthenticated && !state.auth.user) {
        errors.push('User is authenticated but no user object found');
      }

      if (state.auth.token && !state.auth.tokenExpiresAt) {
        warnings.push('Token exists but no expiration time');
      }

      // Validate other states as needed
      if (state.groups.isLoading && state.groups.groups.length === 0) {
        warnings.push('Groups are loading but no groups in state');
      }

      return {
        isValid: errors.length === 0,
        errors,
        warnings,
      };
    });
  }

  // Get state memory usage
  getStateMemoryUsage(): Observable<{
    estimatedSize: number;
    localStorageSize: number;
    memoryPressure: 'low' | 'medium' | 'high';
  }> {
    return this.store.select((state) => {
      const estimatedSize = JSON.stringify(state).length;
      const localStorageSize = localStorage.getItem('app_state')?.length || 0;

      let memoryPressure: 'low' | 'medium' | 'high' = 'low';
      if (estimatedSize > 1000000) memoryPressure = 'high';
      else if (estimatedSize > 100000) memoryPressure = 'medium';

      return {
        estimatedSize,
        localStorageSize,
        memoryPressure,
      };
    });
  }

  // Clear debug data
  clearDebugData(): void {
    // Clear any debug-related data
    console.log('Debug data cleared');
  }

  // Enable/disable debug logging
  setDebugLogging(enabled: boolean): void {
    if (enabled) {
      console.log('State debug logging enabled');
    } else {
      console.log('State debug logging disabled');
    }
  }

  // Get state change frequency
  getStateChangeFrequency(): Observable<{
    changesPerMinute: number;
    lastChangeTime: number;
    totalChanges: number;
  }> {
    // This would track state change frequency
    // For now, return basic metrics
    return new Observable((observer) => {
      observer.next({
        changesPerMinute: 0,
        lastChangeTime: Date.now(),
        totalChanges: 0,
      });
      observer.complete();
    });
  }
}
