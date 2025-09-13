"use client";

import { useState } from "react";
import { useDashboard } from "../model";
import { StatCard } from "./StatCard";
import { QuickActionModal } from "./QuickActionModal";
import { Card } from "./CustomCard";
import { Button } from "./CustomButton";

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
    refetch();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Заголовок */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center space-x-4">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-gray-100 to-gray-200 bg-clip-text text-transparent">
              Панель управления
            </h1>
            <Button
              onClick={refetch}
              disabled={loading}
              loading={loading}
              variant="ghost"
              size="lg"
              className="p-3"
              title="Обновить данные"
            >
              <span className="text-2xl">🔄</span>
            </Button>
          </div>
          <p className="text-lg text-white/70 max-w-2xl mx-auto">
            Добро пожаловать в систему управления парсером комментариев
          </p>
        </div>
        
        {/* Ошибка загрузки */}
        {error && (
          <Card className="bg-red-500/10 border-red-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <span className="text-red-400 text-2xl">⚠️</span>
                <div>
                  <h3 className="text-red-400 font-semibold text-lg">Ошибка загрузки данных</h3>
                  <p className="text-red-300/80 text-sm">{error}</p>
                </div>
              </div>
              <Button
                onClick={refetch}
                disabled={loading}
                loading={loading}
                variant="danger"
                size="md"
              >
                Повторить
              </Button>
            </div>
          </Card>
        )}

        {/* Статистические карточки */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {statsConfig.map((config) => (
            <Card key={config.key}>
              <StatCard
                title={config.title}
                value={stats[config.key] as number}
                growth={stats[config.growthKey] as number}
                icon={config.icon}
                color={config.color}
                loading={loading}
              />
            </Card>
          ))}
        </div>

        {/* Быстрые действия */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
              <span className="mr-2">🚀</span>
              Быстрые действия
            </h3>
            <div className="space-y-3">
              {quickActions.map((action) => (
                <Button
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
                    <span className="text-white/40 group-hover:text-white/60">→</span>
                  </span>
                </Button>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Модальное окно для быстрых действий */}
      <QuickActionModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        action={selectedAction}
      />
    </div>
  );
};