import { User } from '../services/auth.service';
import { VKGroupResponse } from '../models/vk-group.model';
import { KeywordResponse } from '../models/keyword.model';
import { VKCommentResponse } from '../models/vk-comment.model';
import { SystemMetrics } from '../models/monitoring.model';
import { ApplicationSettings } from '../models/settings.model';

// Auth State
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  token: string | null;
  tokenExpiresAt: string | null;
}

// Groups State
export interface GroupsState {
  groups: VKGroupResponse[];
  selectedGroups: VKGroupResponse[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  searchTerm: string;
  filters: {
    status: string | null;
    category: string | null;
    dateRange: { start: string | null; end: string | null };
  };
}

// Keywords State
export interface KeywordsState {
  keywords: KeywordResponse[];
  selectedKeywords: KeywordResponse[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  searchTerm: string;
  filters: {
    category: string | null;
    status: string | null;
    dateRange: { start: string | null; end: string | null };
  };
}

// Comments State
export interface CommentsState {
  comments: VKCommentResponse[];
  selectedComments: VKCommentResponse[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  searchTerm: string;
  filters: {
    status: string | null;
    group: string | null;
    dateRange: { start: string | null; end: string | null };
  };
}

// Monitoring State
export interface MonitoringState {
  systemMetrics: SystemMetrics | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;
  autoRefresh: boolean;
  refreshInterval: number;
}

// Settings State
export interface SettingsState {
  settings: ApplicationSettings | null;
  isLoading: boolean;
  error: string | null;
  isDirty: boolean;
  lastSaved: string | null;
}

// UI State
export interface UIState {
  loading: boolean;
  loadingMessage: string | null;
  notifications: Notification[];
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
}

// Notification interface
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  duration?: number;
  timestamp: string;
}

// Main Application State
export interface AppState {
  auth: AuthState;
  groups: GroupsState;
  keywords: KeywordsState;
  comments: CommentsState;
  monitoring: MonitoringState;
  settings: SettingsState;
  ui: UIState;
}
