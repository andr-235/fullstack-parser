export interface DashboardStats {
  totalComments: number;
  activeGroups: number;
  keywords: number;
  activeParsers: number;
  commentsGrowth: number;
  groupsGrowth: number;
  keywordsGrowth: number;
  parsersGrowth: number;
}

export interface DashboardMetrics {
  comments: {
    total: number;
    growth_percentage: number;
    trend: string;
  };
  groups: {
    active: number;
    growth_percentage: number;
    trend: string;
  };
  keywords: {
    total: number;
    growth_percentage: number;
    trend: string;
  };
  parsers: {
    active: number;
    growth_percentage: number;
    trend: string;
  };
}

export interface StatCardConfig {
  key: keyof DashboardStats;
  growthKey: keyof DashboardStats;
  title: string;
  icon: string;
  color: string;
}

export interface QuickAction {
  label: string;
  icon: string;
}

export interface RecentActivity {
  status: string;
  time: string;
  color: string;
  pulse: boolean;
}
