"use client";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

import { useState, useEffect } from "react";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";
import { GlassCard } from "@/shared/ui/glass-card";

interface DashboardStats {
  totalComments: number;
  activeGroups: number;
  keywords: number;
  activeParsers: number;
  commentsGrowth: number;
  groupsGrowth: number;
  keywordsGrowth: number;
  parsersGrowth: number;
}

export default function DashboardPage() {
  useRouteAccess(); // Проверяем доступ к приватной странице

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
  const statsConfig = [
    {
      key: 'totalComments' as keyof DashboardStats,
      growthKey: 'commentsGrowth' as keyof DashboardStats,
      title: 'Всего комментариев',
      icon: '💬',
      color: 'bg-blue-500',
    },
    {
      key: 'activeGroups' as keyof DashboardStats,
      growthKey: 'groupsGrowth' as keyof DashboardStats,
      title: 'Активных групп',
      icon: '👥',
      color: 'bg-green-500',
    },
    {
      key: 'keywords' as keyof DashboardStats,
      growthKey: 'keywordsGrowth' as keyof DashboardStats,
      title: 'Ключевых слов',
      icon: '🔍',
      color: 'bg-purple-500',
    },
    {
      key: 'activeParsers' as keyof DashboardStats,
      growthKey: 'parsersGrowth' as keyof DashboardStats,
      title: 'Активных парсеров',
      icon: '⚙️',
      color: 'bg-orange-500',
    },
  ];

  // Конфигурация быстрых действий
  const quickActions = [
    { label: 'Добавить новую группу', icon: '➕' },
    { label: 'Настроить ключевые слова', icon: '🔧' },
    { label: 'Запустить парсер', icon: '▶️' },
  ];

  // Конфигурация последней активности
  const recentActivity = [
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

  const StatCard = ({ 
    title, 
    value, 
    growth, 
    icon, 
    color 
  }: {
    title: string;
    value: number;
    growth: number;
    icon: string;
    color: string;
  }) => (
    <div className="group relative overflow-hidden rounded-xl bg-white/5 border border-white/10 p-6 transition-all duration-300 hover:bg-white/10 hover:scale-105">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-xl ${color} bg-opacity-20`}>
            <span className="text-2xl">{icon}</span>
          </div>
          <h3 className="text-sm font-medium text-white/80">{title}</h3>
        </div>
        <div className={`text-xs px-2 py-1 rounded-full ${
          growth >= 0 
            ? 'bg-green-500/20 text-green-400' 
            : 'bg-red-500/20 text-red-400'
        }`}>
          {growth >= 0 ? '+' : ''}{growth}%
        </div>
      </div>
      
      <div className="space-y-1">
        <div className="text-3xl font-bold text-white">
          {loading ? (
            <div className="h-8 w-20 bg-white/20 rounded animate-pulse" />
          ) : (
            value.toLocaleString()
          )}
        </div>
        <p className="text-xs text-white/60">
          {growth >= 0 ? 'рост' : 'снижение'} с прошлого месяца
        </p>
      </div>
    </div>
  );

  return (
    <GlassCard maxWidth="2xl" className="!min-h-screen !py-0">
      <div className="p-6 space-y-8">
        {/* Заголовок */}
        <div className="text-center space-y-4 animate-fade-in-up">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-blue-100 to-cyan-100 bg-clip-text text-transparent">
            Панель управления
          </h1>
          <p className="text-xl text-white/70 max-w-2xl mx-auto">
            Добро пожаловать в систему управления парсером комментариев
          </p>
        </div>
        
        {/* Статистические карточки */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          {statsConfig.map((config) => (
            <StatCard
              key={config.key}
              title={config.title}
              value={stats[config.key] as number}
              growth={stats[config.growthKey] as number}
              icon={config.icon}
              color={config.color}
            />
          ))}
        </div>

        {/* Дополнительная информация */}
        <div className="grid gap-6 md:grid-cols-2 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          {/* Быстрые действия */}
          <div className="bg-white/5 rounded-xl border border-white/10 p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🚀</span>
              Быстрые действия
            </h3>
            <div className="space-y-3">
              {quickActions.map((action, index) => (
                <button 
                  key={index}
                  className="w-full text-left p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors duration-200 flex items-center justify-between group"
                >
                  <span className="text-white/80 group-hover:text-white flex items-center">
                    <span className="mr-2">{action.icon}</span>
                    {action.label}
                  </span>
                  <span className="text-white/40 group-hover:text-white/60">→</span>
                </button>
              ))}
            </div>
          </div>

          {/* Последняя активность */}
          <div className="bg-white/5 rounded-xl border border-white/10 p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">📊</span>
              Последняя активность
            </h3>
            <div className="space-y-3">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-white/5">
                  <div className={`w-2 h-2 ${activity.color} rounded-full ${activity.pulse ? 'animate-pulse' : ''}`} />
                  <div className="flex-1">
                    <p className="text-sm text-white/80">{activity.status}</p>
                    <p className="text-xs text-white/60">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </GlassCard>
  );
}
