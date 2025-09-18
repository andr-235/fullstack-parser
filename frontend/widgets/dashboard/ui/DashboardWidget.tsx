"use client";

import { useState, lazy, Suspense, useCallback, useMemo } from "react";
import { useDashboard } from "../model";
import { StatCard } from "./StatCard";
import { GlassCard } from "@/shared/ui";
import { GlassButton } from "@/shared/ui";

const QuickActionModal = lazy(() => import("./QuickActionModal").then(mod => ({ default: mod.QuickActionModal })));

export const DashboardWidget = () => {
  const { stats, loading, error, statsConfig, quickActions, refetch } = useDashboard();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAction, setSelectedAction] = useState<string>("");

  const handleActionClick = useCallback((action: string) => {
    setSelectedAction(action);
    setIsModalOpen(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setIsModalOpen(false);
    setSelectedAction("");
    refetch();
  }, [refetch]);

  const statsCards = useMemo(() => statsConfig.map((config) => (
    <GlassCard key={config.key}>
      <StatCard
        title={config.title}
        value={stats[config.key]}
        growth={stats[config.growthKey]}
        icon={config.icon}
        color={config.color}
        loading={loading}
      />
    </GlassCard>
  )), [statsConfig, stats, loading]);

  const quickActionButtons = useMemo(() => quickActions.map((action) => (
    <GlassButton
      key={action.label}
      onClick={() => handleActionClick(action.label)}
      variant="ghost"
      className="w-full justify-start p-3 h-auto"
    >
      <span className="flex items-center justify-between w-full">
        <span className="flex items-center">
          <span className="mr-2">{action.icon}</span>
          {action.label}
        </span>
        <span className="text-white/40 hover:text-white/60">→</span>
      </span>
    </GlassButton>
  )), [quickActions, handleActionClick]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Заголовок */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-200 bg-clip-text text-transparent">
              Панель управления
            </h1>
            <GlassButton
              onClick={refetch}
              disabled={loading}
              loading={loading}
              variant="ghost"
              size="lg"
              className="p-3"
            >
              <span className="text-2xl" title="Обновить данные">🔄</span>
            </GlassButton>
          </div>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Добро пожаловать в систему управления парсером комментариев
          </p>
        </div>

        {/* Ошибка загрузки */}
        {error && (
          <GlassCard className="bg-red-500/10 border-red-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-red-400 text-2xl">⚠️</span>
                <div>
                  <h3 className="text-red-400 font-semibold text-lg">Ошибка загрузки данных</h3>
                  <p className="text-red-300/80 text-sm">{error}</p>
                </div>
              </div>
              <GlassButton
                onClick={refetch}
                disabled={loading}
                loading={loading}
                variant="outline"
                size="md"
              >
                Повторить
              </GlassButton>
            </div>
          </GlassCard>
        )}

        {/* Статистические карточки */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {statsCards}
        </div>

        {/* Быстрые действия */}
        <div className="grid gap-6 md:grid-cols-2">
          <GlassCard>
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🚀</span>
              Быстрые действия
            </h3>
            <div className="space-y-3">
              {quickActionButtons}
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Модальное окно для быстрых действий */}
      <Suspense fallback={<div className="flex items-center justify-center p-4"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div></div>}>
        <QuickActionModal
          isOpen={isModalOpen}
          onClose={handleModalClose}
          action={selectedAction}
        />
      </Suspense>
    </div>
  );
};