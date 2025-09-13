"use client";

// Отключаем статическую генерацию для приватных страниц
export const dynamic = 'force-dynamic'

import { useState, useEffect } from "react";

import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

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
    <div className="group relative overflow-hidden rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 p-6 transition-all duration-300 hover:bg-white/15 hover:scale-105 hover:shadow-2xl">
      {/* Декоративный градиент */}
      <div className={`absolute inset-0 opacity-20 ${color} rounded-2xl`} />
      
      <div className="relative z-10">
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
      
      {/* Hover эффект */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
    </div>
  );

  return (
    <div className="min-h-screen relative">
      {/* Фоновый градиент */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900" />
      
      {/* Декоративные элементы */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-600 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse" />
        <div className="absolute top-40 left-1/2 w-60 h-60 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse" />
      </div>

      {/* Основной контент */}
      <div className="relative z-10 p-6 space-y-8">
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
          <StatCard
            title="Всего комментариев"
            value={stats.totalComments}
            growth={stats.commentsGrowth}
            icon="💬"
            color="bg-blue-500"
          />
          
          <StatCard
            title="Активных групп"
            value={stats.activeGroups}
            growth={stats.groupsGrowth}
            icon="👥"
            color="bg-green-500"
          />
          
          <StatCard
            title="Ключевых слов"
            value={stats.keywords}
            growth={stats.keywordsGrowth}
            icon="🔍"
            color="bg-purple-500"
          />
          
          <StatCard
            title="Активных парсеров"
            value={stats.activeParsers}
            growth={stats.parsersGrowth}
            icon="⚙️"
            color="bg-orange-500"
          />
        </div>

        {/* Дополнительная информация */}
        <div className="grid gap-6 md:grid-cols-2 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          {/* Быстрые действия */}
          <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🚀</span>
              Быстрые действия
            </h3>
            <div className="space-y-3">
              <button className="w-full text-left p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors duration-200 flex items-center justify-between group">
                <span className="text-white/80 group-hover:text-white">Добавить новую группу</span>
                <span className="text-white/40 group-hover:text-white/60">→</span>
              </button>
              <button className="w-full text-left p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors duration-200 flex items-center justify-between group">
                <span className="text-white/80 group-hover:text-white">Настроить ключевые слова</span>
                <span className="text-white/40 group-hover:text-white/60">→</span>
              </button>
              <button className="w-full text-left p-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors duration-200 flex items-center justify-between group">
                <span className="text-white/80 group-hover:text-white">Запустить парсер</span>
                <span className="text-white/40 group-hover:text-white/60">→</span>
              </button>
            </div>
          </div>

          {/* Последняя активность */}
          <div className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 p-6">
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">📊</span>
              Последняя активность
            </h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-3 rounded-xl bg-white/5">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <div className="flex-1">
                  <p className="text-sm text-white/80">Парсер запущен</p>
                  <p className="text-xs text-white/60">2 минуты назад</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 rounded-xl bg-white/5">
                <div className="w-2 h-2 bg-blue-400 rounded-full" />
                <div className="flex-1">
                  <p className="text-sm text-white/80">Новые комментарии найдены</p>
                  <p className="text-xs text-white/60">15 минут назад</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-3 rounded-xl bg-white/5">
                <div className="w-2 h-2 bg-yellow-400 rounded-full" />
                <div className="flex-1">
                  <p className="text-sm text-white/80">Обновлены ключевые слова</p>
                  <p className="text-xs text-white/60">1 час назад</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
