"use client";

import { useState, useEffect, useCallback } from 'react';
import { ParserFormData, ParsingTask, ParserStats } from '@/entities/parser';
import { parserApi } from '@/shared/api/parser';

export const useParserPage = () => {
  // Form state
  const [formData, setFormData] = useState<ParserFormData>({
    group_ids: '',
    max_posts: 10,
    max_comments_per_post: 100,
    force_reparse: false,
    priority: 'normal',
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Tasks state
  const [tasks, setTasks] = useState<ParsingTask[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [tasksError, setTasksError] = useState<string | null>(null);

  // Stats state
  const [stats, setStats] = useState<ParserStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    handleTaskRefresh();
    handleStatsRefresh();
  }, []);

  // Form handlers
  const handleFormChange = useCallback((field: keyof ParserFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleFormSubmit = useCallback(async (data: ParserFormData) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const groupIds = data.group_ids
        .split(',')
        .map(id => parseInt(id.trim()))
        .filter(id => !isNaN(id));

      if (groupIds.length === 0) {
        throw new Error('Необходимо указать хотя бы один ID группы');
      }

      await parserApi.startBulkParse({
        group_ids: groupIds,
        max_posts: data.max_posts,
        max_comments_per_post: data.max_comments_per_post,
        force_reparse: data.force_reparse,
        priority: data.priority,
      });

      // Reset form
      setFormData({
        group_ids: '',
        max_posts: 10,
        max_comments_per_post: 100,
        force_reparse: false,
        priority: 'normal',
      });

      // Refresh tasks list
      await handleTaskRefresh();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Произошла ошибка при запуске парсинга');
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  // Tasks handlers
  const handleTaskRefresh = useCallback(async () => {
    setTasksLoading(true);
    setTasksError(null);

    try {
      const response = await parserApi.getTasks();
      setTasks(response.tasks);
    } catch (error) {
      setTasksError(error instanceof Error ? error.message : 'Ошибка загрузки задач');
    } finally {
      setTasksLoading(false);
    }
  }, []);

  const handleTaskStop = useCallback(async (taskId: string) => {
    try {
      await parserApi.stopParse(taskId, { task_id: taskId });
      await handleTaskRefresh();
    } catch (error) {
      console.error('Error stopping task:', error);
    }
  }, [handleTaskRefresh]);

  // Stats handlers
  const handleStatsRefresh = useCallback(async () => {
    setStatsLoading(true);
    setStatsError(null);

    try {
      const response = await parserApi.getParserStats();
      setStats(response);
    } catch (error) {
      setStatsError(error instanceof Error ? error.message : 'Ошибка загрузки статистики');
    } finally {
      setStatsLoading(false);
    }
  }, []);

  return {
    // Form state
    formData,
    isSubmitting,
    submitError,

    // Tasks state
    tasks,
    tasksLoading,
    tasksError,

    // Stats state
    stats,
    statsLoading,
    statsError,

    // Actions
    handleFormSubmit,
    handleFormChange,
    handleTaskStop,
    handleTaskRefresh,
    handleStatsRefresh,
  };
};