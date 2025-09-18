import { useState, useEffect, useCallback } from 'react';
import { ParsingTask } from '@/entities/parser';
import { useParserApi } from './useParserApi';

interface UseParserTasksOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export const useParserTasks = (options: UseParserTasksOptions = {}) => {
  const { autoRefresh = false, refreshInterval = 5000 } = options;
  const [tasks, setTasks] = useState<ParsingTask[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { getTasks } = useParserApi();

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Не удалось загрузить задачи');
      console.error('Failed to fetch tasks:', err);
    } finally {
      setLoading(false);
    }
  }, [getTasks]);

  const refetch = useCallback(() => {
    fetchTasks();
  }, [fetchTasks]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchTasks();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchTasks]);

  return {
    tasks,
    loading,
    error,
    refetch,
  };
};