import { useState, useEffect } from "react";
import type { DashboardStats, StatCardConfig, QuickAction, DashboardMetrics } from "./types";
import { getDashboardMetrics } from "../api";

const STATS_CONFIG: StatCardConfig[] = [
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

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'Добавить новую группу', icon: '➕' },
  { label: 'Настроить ключевые слова', icon: '🔧' },
  { label: 'Запустить парсер', icon: '▶️' },
];

const transformMetricsToStats = (metrics: DashboardMetrics): DashboardStats => ({
  totalComments: metrics.comments.total,
  activeGroups: metrics.groups.active,
  keywords: metrics.keywords.total,
  activeParsers: metrics.parsers.active,
  commentsGrowth: metrics.comments.growth_percentage,
  groupsGrowth: metrics.groups.growth_percentage,
  keywordsGrowth: metrics.keywords.growth_percentage,
  parsersGrowth: metrics.parsers.growth_percentage,
});

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
    statsConfig: STATS_CONFIG,
    quickActions: QUICK_ACTIONS,
    refetch: fetchMetrics,
  };
};