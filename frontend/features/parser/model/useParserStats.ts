import { useState, useEffect, useCallback } from 'react';
import { ParserStats } from '@/entities/parser';
import { useParserApi } from './useParserApi';

interface UseParserStatsOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useParserStats = (options: UseParserStatsOptions = {}) => {
  const { autoRefresh = false, refreshInterval = 10000 } = options;
  const [stats, setStats] = useState<ParserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { getStats } = useParserApi();

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить статистику');
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  }, [getStats]);

  const refetch = useCallback(() => {
    fetchStats();
  }, [fetchStats]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchStats();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchStats]);

  return {
    stats,
    loading,
    error,
    refetch,
  };
};