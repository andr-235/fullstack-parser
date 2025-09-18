'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs';
import { ParserForm } from './ParserForm';
import { ParserTaskList } from './ParserTaskList';
import { ParserStatsWidget } from './ParserStatsWidget';
import { useParserPage } from '../model/useParserPage';

export const ParserPage: React.FC = () => {
  const {
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
  } = useParserPage();

  return (
    <div className="space-y-6">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Парсер VK</h1>
        <p className="text-muted-foreground">
          Инструмент для сбора и анализа данных из групп VK
        </p>
      </div>

      <Tabs defaultValue="parse" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="parse">Запуск парсинга</TabsTrigger>
          <TabsTrigger value="tasks">Задачи</TabsTrigger>
          <TabsTrigger value="stats">Статистика</TabsTrigger>
        </TabsList>

        <TabsContent value="parse" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Настройка парсинга</CardTitle>
              <CardDescription>
                Укажите параметры для сбора данных из групп VK
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ParserForm
                formData={formData}
                isSubmitting={isSubmitting}
                error={submitError}
                onSubmit={handleFormSubmit}
                onChange={handleFormChange}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Активные задачи</CardTitle>
              <CardDescription>
                Список выполняющихся и завершенных задач парсинга
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ParserTaskList
                tasks={tasks}
                loading={tasksLoading}
                error={tasksError}
                onStopTask={handleTaskStop}
                onRefresh={handleTaskRefresh}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-6">
          <ParserStatsWidget
            stats={stats}
            loading={statsLoading}
            error={statsError}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};