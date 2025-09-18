import { useState, useEffect, useCallback } from 'react';

interface DashboardMetrics {
  today_comments: number;
  week_comments: number;
  today_matches: number;
  week_matches: number;
  match_rate: number;
}

export const useDashboardMetrics = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    today_comments: 0,
    week_comments: 0,
    today_matches: 0,
    week_matches: 0,
    match_rate: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for now - replace with actual API call
      setMetrics({
        today_comments: 123,
        week_comments: 567,
        today_matches: 45,
        week_matches: 234,
        match_rate: 12.5,
      });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch dashboard metrics';
      setError(errorMessage);
      console.error('Failed to fetch dashboard metrics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, []);

  return {
    metrics,
    loading,
    error,
    refetch: fetchMetrics,
  };
};