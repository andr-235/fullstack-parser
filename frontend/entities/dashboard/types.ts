// Dashboard types
export interface RecentActivityItem {
  id: string;
  type: 'comment' | 'post' | 'group' | 'match';
  message: string;
  timestamp: string;
  userId?: string;
}

export interface TopItem {
  name: string;
  count: number;
  id: string;
}

export interface DashboardTopItem {
  name: string;
  count: number;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}