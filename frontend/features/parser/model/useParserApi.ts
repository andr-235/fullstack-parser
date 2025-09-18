"use client";

import { useState, useCallback } from 'react';
import { ParsingTask, ParserStats, ParserState } from '@/entities/parser';

interface CreateTaskParams {
  group_ids: number[];
  max_posts?: number;
  max_comments_per_post?: number;
  force_reparse?: boolean;
  priority?: 'low' | 'normal' | 'high';
}

interface UseParserApiReturn {
  createTask: (params: CreateTaskParams) => Promise<string>;
  getTasks: () => Promise<ParsingTask[]>;
  getTask: (taskId: string) => Promise<ParsingTask>;
  stopTask: (taskId: string) => Promise<void>;
  getStats: () => Promise<ParserStats>;
  getState: () => Promise<ParserState>;
  loading: boolean;
  error: string | null;
}

export const useParserApi = (): UseParserApiReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiRequest = useCallback(async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/parser${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTask = useCallback(async (params: CreateTaskParams): Promise<string> => {
    const response = await apiRequest<{ task_id: string }>('/parse', {
      method: 'POST',
      body: JSON.stringify(params),
    });
    return response.task_id;
  }, [apiRequest]);

  const getTasks = useCallback(async (): Promise<ParsingTask[]> => {
    const response = await apiRequest<{ tasks: ParsingTask[] }>('/tasks');
    return response.tasks;
  }, [apiRequest]);

  const getTask = useCallback(async (taskId: string): Promise<ParsingTask> => {
    const response = await apiRequest<{ task: ParsingTask }>(`/status/${taskId}`);
    return response.task;
  }, [apiRequest]);

  const stopTask = useCallback(async (taskId: string): Promise<void> => {
    await apiRequest('/stop', {
      method: 'POST',
      body: JSON.stringify({ task_id: taskId }),
    });
  }, [apiRequest]);

  const getStats = useCallback(async (): Promise<ParserStats> => {
    return await apiRequest<ParserStats>('/stats');
  }, [apiRequest]);

  const getState = useCallback(async (): Promise<ParserState> => {
    return await apiRequest<ParserState>('/state');
  }, [apiRequest]);

  return {
    createTask,
    getTasks,
    getTask,
    stopTask,
    getStats,
    getState,
    loading,
    error,
  };
};