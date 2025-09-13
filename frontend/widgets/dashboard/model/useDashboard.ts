import { useState, useEffect } from "react";
import type { DashboardStats, StatCardConfig, QuickAction, RecentActivity, DashboardMetrics } from "./types";
import { getDashboardMetrics } from "../api";

export const useDashboard = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalComments: 0,
    activeGroups: 0,
    keywords: 0,
    activeParsers: 0,
    commentsGrowth: 0,
    groupsGrowth: 0,
    keywordsGrowth: 0,
    parsersGrowth: 0,
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Конфигурация статистических карточек
  const statsConfig: StatCardConfig[] = [
    {
      key: 'totalComments',
      growthKey: 'commentsGrowth',
      title: 'Всего комментариев',
      icon: '💬',
      color: 'bg-blue-500',
    },
    {
      key: 'activeGroups',
      growthKey: 'groupsGrowth',
      title: 'Активных групп',
      icon: '👥',
      color: 'bg-green-500',
    },
    {
      key: 'keywords',
      growthKey: 'keywordsGrowth',
      title: 'Ключевых слов',
      icon: '🔍',
      color: 'bg-purple-500',
    },
    {
      key: 'activeParsers',
      growthKey: 'parsersGrowth',
      title: 'Активных парсеров',
      icon: '⚙️',
      color: 'bg-orange-500',
    },
  ];

  // Конфигурация быстрых действий
  const quickActions: QuickAction[] = [
    { label: 'Добавить новую группу', icon: '➕' },
    { label: 'Настроить ключевые слова', icon: '🔧' },
    { label: 'Запустить парсер', icon: '▶️' },
  ];

  // Конфигурация последней активности
  const recentActivity: RecentActivity[] = [
    {
      status: 'Парсер запущен',
      time: '2 минуты назад',
      color: 'bg-green-400',
      pulse: true,
    },
    {
      status: 'Новые комментарии найдены',
      time: '15 минут назад',
      color: 'bg-blue-400',
      pulse: false,
    },
    {
      status: 'Обновлены ключевые слова',
      time: '1 час назад',
      color: 'bg-yellow-400',
      pulse: false,
    },
  ];

  // Функция для преобразования API данных в формат компонента
  const transformMetricsToStats = (metrics: DashboardMetrics): DashboardStats => {
    return {
      totalComments: metrics.comments.total,
      activeGroups: metrics.groups.active,
      keywords: metrics.keywords.total,
      activeParsers: metrics.parsers.active,
      commentsGrowth: metrics.comments.growth_percentage,
      groupsGrowth: metrics.groups.growth_percentage,
      keywordsGrowth: metrics.keywords.growth_percentage,
      parsersGrowth: metrics.parsers.growth_percentage,
    };
  };

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const metrics = await getDashboardMetrics();
      const transformedStats = transformMetricsToStats(metrics);
      
      setStats(transformedStats);
    } catch (err) {
      console.error('Ошибка загрузки метрик:', err);
      setError(err instanceof Error ? err.message : 'Ошибка загрузки данных');
      
      // Fallback к нулевым данным при ошибке
      setStats({
        totalComments: 0,
        activeGroups: 0,
        keywords: 0,
        activeParsers: 0,
        commentsGrowth: 0,
        groupsGrowth: 0,
        keywordsGrowth: 0,
        parsersGrowth: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return {
    stats,
    loading,
    error,
    statsConfig,
    quickActions,
    recentActivity,
    refetch: fetchMetrics,
  };
};
