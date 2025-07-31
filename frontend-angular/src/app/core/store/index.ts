import { ActionReducerMap } from '@ngrx/store';
import { AppState } from './app.state';
import { authReducer } from './auth/auth.reducer';

export const reducers: ActionReducerMap<AppState> = {
  auth: authReducer,
  // Add other reducers here as they are implemented
  groups: (state: any) => state, // Placeholder
  keywords: (state: any) => state, // Placeholder
  comments: (state: any) => state, // Placeholder
  monitoring: (state: any) => state, // Placeholder
  settings: (state: any) => state, // Placeholder
  ui: (state: any) => state, // Placeholder
};
