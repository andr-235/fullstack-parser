"use client";

import { useState } from "react";
import { GlassCard } from "@/shared/ui/glass-card";
import { useDashboard } from "../model";
import { StatCard } from "./StatCard";
import { QuickActionModal } from "./QuickActionModal";

export const DashboardWidget = () => {
  const { stats, loading, error, statsConfig, quickActions, refetch } = useDashboard();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAction, setSelectedAction] = useState<string>("");

  const handleActionClick = (action: string) => {
    setSelectedAction(action);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setSelectedAction("");
    refetch(); // Обновляем данные после выполнения действия
  };

  return (
    <GlassCard className="!min-h-screen !py-0 !max-w-none !w-full !items-start !justify-start">
      <div className="p-6 space-y-8 w-full">
        {/* Заголовок */}
        <div className="text-center space-y-4 animate-fade-in-up">
          <div className="flex items-center justify-center space-x-4">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-white via-blue-100 to-cyan-100 bg-clip-text text-transparent">
              Панель управления
            </h1>
            <button
              onClick={refetch}
              disabled={loading}
              className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Обновить данные"
            >
              <span className={`text-white text-xl ${loading ? 'animate-spin' : ''}`}>
                🔄
              </span>
            </button>
          </div>
          <p className="text-xl text-white/70 max-w-2xl mx-auto">
            Добро пожаловать в систему управления парсером комментариев
          </p>
        </div>
        
        {/* Ошибка загрузки */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 animate-fade-in-up">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-red-400 text-xl">⚠️</span>
                <div>
                  <h3 className="text-red-400 font-semibold">Ошибка загрузки данных</h3>
                  <p className="text-red-300/80 text-sm">{error}</p>
                </div>
              </div>
              <button
                onClick={refetch}
                disabled={loading}
                className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Загрузка...' : 'Повторить'}
              </button>
            </div>
          </div>
        )}

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
                  onClick={() => handleActionClick(action.label)}
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

        </div>
      </div>

      {/* Модальное окно для быстрых действий */}
      <QuickActionModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        action={selectedAction}
      />
    </GlassCard>
  );
};
