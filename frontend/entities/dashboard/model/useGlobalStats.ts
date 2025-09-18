import { useState, useEffect, useCallback } from 'react';

export interface GlobalStats {
  totalPosts: number;
  totalComments: number;
  activeParsers: number;
  lastActivity: string;
  active_groups: number;
  active_keywords: number;
  total_groups: number;
  total_keywords: number;
  comments_with_keywords: number;
}

export const useGlobalStats = () => {
  const [stats, setStats] = useState<GlobalStats>({
    totalPosts: 0,
    totalComments: 0,
    activeParsers: 0,
    lastActivity: new Date().toISOString(),
    active_groups: 0,
    active_keywords: 0,
    total_groups: 0,
    total_keywords: 0,
    comments_with_keywords: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for now - replace with actual API call
      setStats({
        totalPosts: 1250,
        totalComments: 5432,
        activeParsers: 2,
        lastActivity: new Date().toISOString(),
        active_groups: 8,
        active_keywords: 15,
        total_groups: 20,
        total_keywords: 50,
        comments_with_keywords: 1234,
      });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch global stats');
      console.error('Failed to fetch global stats:', err);
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