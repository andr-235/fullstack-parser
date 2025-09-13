import { useState, useEffect } from "react";
import type { DashboardStats, StatCardConfig, QuickAction, RecentActivity } from "./types";

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

  useEffect(() => {
    // Симуляция загрузки данных
    const timer = setTimeout(() => {
      setStats({
        totalComments: 1247,
        activeGroups: 23,
        keywords: 156,
        activeParsers: 8,
        commentsGrowth: 12.5,
        groupsGrowth: 8.2,
        keywordsGrowth: 15.3,
        parsersGrowth: -2.1,
      });
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return {
    stats,
    loading,
    statsConfig,
    quickActions,
    recentActivity,
  };
};
