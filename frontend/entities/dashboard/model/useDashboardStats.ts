import { useState, useEffect, useCallback } from 'react';
import type { RecentActivityItem, TopItem } from '../types';

export interface DashboardStats {
  today_comments: number;
  today_matches: number;
  week_comments: number;
  week_matches: number;
  recent_activity: RecentActivityItem[];
  top_groups: TopItem[];
  top_keywords: TopItem[];
  postsToday: number;
  commentsToday: number;
  activeGroups: number;
  systemHealth: 'good' | 'warning' | 'error';
}

export const useDashboardStats = () => {
  const [stats, setStats] = useState<DashboardStats>({
    today_comments: 0,
    today_matches: 0,
    week_comments: 0,
    week_matches: 0,
    recent_activity: [],
    top_groups: [],
    top_keywords: [],
    postsToday: 0,
    commentsToday: 0,
    activeGroups: 0,
    systemHealth: 'good',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for now - replace with actual API call
      setStats({
        today_comments: 123,
        today_matches: 45,
        week_comments: 567,
        week_matches: 234,
        recent_activity: [],
        top_groups: [],
        top_keywords: [],
        postsToday: 45,
        commentsToday: 123,
        activeGroups: 8,
        systemHealth: 'good',
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard stats';
      setError(errorMessage);
      console.error('Failed to fetch dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, []);

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
};