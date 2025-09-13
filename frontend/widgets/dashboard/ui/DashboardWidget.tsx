"use client";

import { GlassCard } from "@/shared/ui/glass-card";
import { useDashboard } from "../model";
import { StatCard } from "./StatCard";

export const DashboardWidget = () => {
  const { stats, loading, statsConfig, quickActions, recentActivity } = useDashboard();

  return (
    <GlassCard className="!min-h-screen !py-0 !max-w-none !w-full !items-start !justify-start">
      <div className="p-6 space-y-8 w-full">
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
              loading={loading}
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
};
