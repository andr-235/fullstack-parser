import { useState, useEffect, useCallback } from 'react';

interface Trend {
  is_positive: boolean;
  today_vs_average: number;
}

interface Trends {
  comments_trend: Trend;
  matches_trend: Trend;
}

export const useTrends = () => {
  const [trends, setTrends] = useState<Trends>({
    comments_trend: {
      is_positive: true,
      today_vs_average: 15,
    },
    matches_trend: {
      is_positive: false,
      today_vs_average: -5,
    },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTrends = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Mock data for now - replace with actual API call
      setTrends({
        comments_trend: {
          is_positive: true,
          today_vs_average: 15,
        },
        matches_trend: {
          is_positive: false,
          today_vs_average: -5,
        },
      });
    } catch (err: any) {
      setError(err.message || 'Failed to fetch trends');
      console.error('Failed to fetch trends:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTrends();
  }, []);

  return {
    trends,
    loading,
    error,
    refetch: fetchTrends,
  };
};