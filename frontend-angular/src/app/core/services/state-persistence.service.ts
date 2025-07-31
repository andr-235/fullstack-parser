import { Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable, filter, map } from 'rxjs';
import { AppState } from '../store/app.state';

@Injectable({
  providedIn: 'root',
})
export class StatePersistenceService {
  private readonly STORAGE_KEY = 'app_state';

  constructor(private store: Store<AppState>) {}

  // Save state to localStorage
  saveState(state: Partial<AppState>): void {
    try {
      const serializedState = JSON.stringify(state);
      localStorage.setItem(this.STORAGE_KEY, serializedState);
    } catch (error) {
      console.error('Error saving state to localStorage:', error);
    }
  }

  // Load state from localStorage
  loadState(): Partial<AppState> | null {
    try {
      const serializedState = localStorage.getItem(this.STORAGE_KEY);
      if (serializedState) {
        return JSON.parse(serializedState);
      }
    } catch (error) {
      console.error('Error loading state from localStorage:', error);
    }
    return null;
  }

  // Clear state from localStorage
  clearState(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.error('Error clearing state from localStorage:', error);
    }
  }

  // Save specific part of state
  saveStatePart(key: keyof AppState, data: any): void {
    try {
      const currentState = this.loadState() || {};
      const updatedState = { ...currentState, [key]: data };
      this.saveState(updatedState);
    } catch (error) {
      console.error(`Error saving state part ${key}:`, error);
    }
  }

  // Load specific part of state
  loadStatePart<T>(key: keyof AppState): T | null {
    try {
      const state = this.loadState();
      return state ? (state[key] as T) : null;
    } catch (error) {
      console.error(`Error loading state part ${key}:`, error);
      return null;
    }
  }

  // Auto-save state changes
  setupAutoSave(): void {
    // This would be implemented to watch for state changes and auto-save
    // For now, it's a placeholder for future implementation
  }

  // Export state for debugging
  exportState(): string {
    try {
      const state = this.loadState();
      return JSON.stringify(state, null, 2);
    } catch (error) {
      console.error('Error exporting state:', error);
      return '{}';
    }
  }

  // Import state from string
  importState(stateString: string): boolean {
    try {
      const state = JSON.parse(stateString);
      this.saveState(state);
      return true;
    } catch (error) {
      console.error('Error importing state:', error);
      return false;
    }
  }

  // Get state size for monitoring
  getStateSize(): number {
    try {
      const serializedState = localStorage.getItem(this.STORAGE_KEY);
      return serializedState ? serializedState.length : 0;
    } catch (error) {
      console.error('Error getting state size:', error);
      return 0;
    }
  }

  // Check if state is valid
  isStateValid(): boolean {
    try {
      const state = this.loadState();
      return state !== null && typeof state === 'object';
    } catch (error) {
      return false;
    }
  }

  // Migrate state (for version updates)
  migrateState(currentVersion: string, targetVersion: string): boolean {
    try {
      const state = this.loadState();
      if (!state) return true;

      // Add migration logic here when needed
      // For now, just return true
      return true;
    } catch (error) {
      console.error('Error migrating state:', error);
      return false;
    }
  }
}
