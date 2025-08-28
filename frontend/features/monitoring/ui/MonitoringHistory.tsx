'use client'

import { useState } from 'react'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'
import {
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertTriangle,
  Calendar,
  Activity,
} from 'lucide-react'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

interface MonitoringHistoryProps {
  // Здесь будут данные истории мониторинга
  // Пока используем заглушки
}

export default function MonitoringHistory({ }: MonitoringHistoryProps) {
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('7d')

  // Заглушечные данные для демонстрации
  const mockData = {
    totalRuns: 156,
    successfulRuns: 142,
    failedRuns: 14,
    averageDuration: 45,
    totalGroupsMonitored: 25,
    lastRun: new Date(),
    runsByDay: [
      { date: '2025-01-10', runs: 12, success: 11, failed: 1 },
      { date: '2025-01-11', runs: 15, success: 14, failed: 1 },
      { date: '2025-01-12', runs: 18, success: 17, failed: 1 },
      { date: '2025-01-13', runs: 14, success: 13, failed: 1 },
      { date: '2025-01-14', runs: 16, success: 15, failed: 1 },
      { date: '2025-01-15', runs: 20, success: 19, failed: 1 },
      { date: '2025-01-16', runs: 22, success: 21, failed: 1 },
    ],
    recentErrors: [
      {
        id: 1,
        groupName: 'Тестовая группа 1',
        error: 'Rate limit exceeded',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 часа назад
      },
      {
        id: 2,
        groupName: 'Тестовая группа 2',
        error: 'Network timeout',
        timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 часа назад
      },
    ],
  }

  const successRate = Math.round(
    (mockData.successfulRuns / mockData.totalRuns) * 100
  )

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <BarChart3 className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-200">
              История мониторинга
            </h2>
            <p className="text-sm text-slate-400">
              Статистика и аналитика работы системы мониторинга
            </p>
          </div>
        </div>

        {/* Фильтр по времени */}
        <div className="flex space-x-2">
          {[
            { key: '24h', label: '24 часа' },
            { key: '7d', label: '7 дней' },
            { key: '30d', label: '30 дней' },
          ].map((range) => (
            <button
              key={range.key}
              onClick={() => setTimeRange(range.key as any)}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${timeRange === range.key
                ? 'bg-blue-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-slate-700 bg-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Всего запусков</p>
                <p className="text-2xl font-bold text-blue-400">
                  {mockData.totalRuns}
                </p>
              </div>
              <Activity className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-700 bg-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Успешных</p>
                <p className="text-2xl font-bold text-green-400">
                  {mockData.successfulRuns}
                </p>
                <p className="text-xs text-slate-400">
                  {successRate}% успешность
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-700 bg-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Ошибок</p>
                <p className="text-2xl font-bold text-red-400">
                  {mockData.failedRuns}
                </p>
                <p className="text-xs text-slate-400">
                  {Math.round((mockData.failedRuns / mockData.totalRuns) * 100)}
                  % ошибок
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-700 bg-slate-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Среднее время</p>
                <p className="text-2xl font-bold text-purple-400">
                  {mockData.averageDuration}с
                </p>
                <p className="text-xs text-slate-400">на группу</p>
              </div>
              <Clock className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Вкладки с детальной информацией */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Обзор
          </TabsTrigger>
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Временная шкала
          </TabsTrigger>
          <TabsTrigger value="errors" className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Ошибки
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <Card className="border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-400" />
                Статистика по дням
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockData.runsByDay.map((day, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-slate-700 rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="text-sm font-medium text-slate-300">
                        {(() => {
                          try {
                            const date = new Date(day.date)
                            return isNaN(date.getTime())
                              ? 'Неверная дата'
                              : format(date, 'dd MMM', { locale: ru })
                          } catch {
                            return 'Неверная дата'
                          }
                        })()}
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge
                          variant="outline"
                          className="bg-green-600 text-white"
                        >
                          {day.success}
                        </Badge>
                        <Badge
                          variant="outline"
                          className="bg-red-600 text-white"
                        >
                          {day.failed}
                        </Badge>
                      </div>
                    </div>
                    <div className="text-sm text-slate-400">
                      Всего: {day.runs}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <Card className="border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-400" />
                Временная шкала активности
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center py-8">
                  <div className="p-4 bg-slate-700 rounded-full inline-block mb-4">
                    <TrendingUp className="h-8 w-8 text-slate-400" />
                  </div>
                  <p className="text-slate-400 font-medium">
                    График активности
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    Детальная визуализация будет добавлена в следующем
                    обновлении
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="errors" className="space-y-4">
          <Card className="border-slate-700 bg-slate-800">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                Последние ошибки
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockData.recentErrors.length > 0 ? (
                  mockData.recentErrors.map((error) => (
                    <div
                      key={error.id}
                      className="p-4 bg-slate-700 rounded-lg border-l-4 border-red-500"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <AlertTriangle className="h-4 w-4 text-red-400" />
                            <span className="font-medium text-slate-200">
                              {error.groupName}
                            </span>
                          </div>
                          <p className="text-sm text-slate-300 mb-2">
                            {error.error}
                          </p>
                          <p className="text-xs text-slate-400">
                            {format(error.timestamp, 'dd.MM.yyyy HH:mm', {
                              locale: ru,
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <div className="p-4 bg-slate-700 rounded-full inline-block mb-4">
                      <CheckCircle className="h-8 w-8 text-green-400" />
                    </div>
                    <p className="text-slate-400 font-medium">Ошибок нет</p>
                    <p className="text-sm text-slate-500 mt-1">
                      Система работает стабильно
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
