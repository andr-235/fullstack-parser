'use client'

import React, { useState, useEffect } from 'react'
import {
  useParserState,
  useParserStats,
  useStartParser,
  useStopParser,
  useRecentRuns,
} from '@/hooks/use-parser'
import { useGroups } from '@/hooks/use-groups'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge, BadgeProps } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import {
  Play,
  Pause,
  Server,
  Timer,
  CheckCircle2,
  XCircle,
  History,
  Settings,
  Activity,
  Clock,
  Target,
} from 'lucide-react'
import { Progress } from '@/components/ui/progress'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { ParseTaskResponse } from '@/types/api'

const statusConfig: Record<
  string,
  { label: string; variant: BadgeProps['variant']; icon: React.ElementType; color: string }
> = {
  running: {
    label: 'В работе',
    variant: 'default',
    icon: Play,
    color: 'bg-green-900 text-green-300 border-green-700'
  },
  completed: {
    label: 'Завершен',
    variant: 'default',
    icon: CheckCircle2,
    color: 'bg-blue-900 text-blue-300 border-blue-700'
  },
  failed: {
    label: 'Ошибка',
    variant: 'destructive',
    icon: XCircle,
    color: 'bg-red-900 text-red-300 border-red-700'
  },
  stopped: {
    label: 'Остановлен',
    variant: 'secondary',
    icon: Pause,
    color: 'bg-slate-700 text-slate-300 border-slate-600'
  },
}

const ParserStatus = ({ status }: { status: string }) => {
  const config = statusConfig[status] || statusConfig.stopped
  return (
    <Badge className={`flex items-center gap-1.5 ${config.color}`}>
      <config.icon className="h-3 w-3" />
      <span>{config.label}</span>
    </Badge>
  )
}

export default function ParserPage() {
  const [selectedGroupId, setSelectedGroupId] = useState<string>('')
  const [isProcessing, setIsProcessing] = useState(false)
  const { data: state, isLoading: isLoadingState } = useParserState()
  const { data: stats, isLoading: isLoadingStats } = useParserStats()
  const { data: history, isLoading: isLoadingHistory } = useRecentRuns()
  const { data: groupsData } = useGroups()
  const startParserMutation = useStartParser()
  const stopParserMutation = useStopParser()

  // Сброс состояния обработки после завершения мутации
  useEffect(() => {
    if (!startParserMutation.isPending && isProcessing) {
      setIsProcessing(false)
    }
  }, [startParserMutation.isPending, isProcessing])

  const handleStart = () => {
    if (selectedGroupId) {
      setIsProcessing(true)
      startParserMutation.mutate({ group_id: Number(selectedGroupId) })
    }
  }

  const isActionInProgress =
    isLoadingState ||
    startParserMutation.isPending ||
    stopParserMutation.isPending ||
    isProcessing

  const groups = groupsData?.items || []

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <Settings className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold">Управление парсером</h1>
        </div>
        <p className="text-slate-300">
          Запускайте и контролируйте процесс парсинга групп VK
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Activity className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Всего запусков</p>
                <p className="text-2xl font-bold text-blue-400">{stats?.total_runs || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Успешных</p>
                <p className="text-2xl font-bold text-green-400">{stats?.successful_runs || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <XCircle className="h-5 w-5 text-red-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Неуспешных</p>
                <p className="text-2xl font-bold text-red-400">{stats?.failed_runs || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Clock className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Среднее время</p>
                <p className="text-2xl font-bold text-purple-400">{Math.round(stats?.average_duration || 0)}с</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Control Panel */}
        <div className="md:col-span-1 space-y-6">
          <Card className="border-slate-700 bg-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200">
                Управление парсером
              </CardTitle>
              <CardDescription className="text-slate-400">
                Запустите или остановите процесс парсинга.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-700 border border-slate-600 rounded-lg">
                <span className="text-sm font-medium text-slate-300">Статус</span>
                <ParserStatus status={state?.status || 'stopped'} />
              </div>

              {state?.status === 'running' && state.task ? (
                <div className="space-y-3 p-3 bg-slate-700 border border-slate-600 rounded-lg">
                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-blue-400" />
                    <p className="text-sm font-medium text-slate-200">
                      Обработка: {state.task.group_name}
                    </p>
                  </div>
                  <Progress
                    value={state.task.progress}
                    className="w-full bg-slate-600"
                  />
                  <p className="text-xs text-slate-400">
                    {state.task.posts_processed} постов обработано
                  </p>
                </div>
              ) : (
                <Select
                  onValueChange={setSelectedGroupId}
                  defaultValue={selectedGroupId}
                >
                  <SelectTrigger className="border-slate-600 bg-slate-700 text-slate-200">
                    <SelectValue placeholder="Выберите группу" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-800 border-slate-600">
                    {groups.map((group) => (
                      <SelectItem key={group.id} value={String(group.id)} className="text-slate-200 hover:bg-slate-700">
                        {group.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {state?.status === 'running' ? (
                <Button
                  className="w-full bg-red-600 hover:bg-red-700 text-white transition-all duration-200 hover:scale-105"
                  onClick={() => stopParserMutation.mutate()}
                  disabled={isActionInProgress}
                >
                  <Pause className="mr-2 h-4 w-4" />
                  Остановить
                </Button>
              ) : (
                <Button
                  className={`w-full flex items-center justify-center gap-2 transition-all duration-200 hover:scale-105 ${isProcessing || startParserMutation.isPending
                      ? 'bg-yellow-600 hover:bg-yellow-700 cursor-wait'
                      : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                  onClick={handleStart}
                  disabled={!selectedGroupId || isActionInProgress}
                >
                  {isProcessing || startParserMutation.isPending ? (
                    <LoadingSpinner size="sm" className="mr-2 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}
                  {isProcessing || startParserMutation.isPending ? (
                    <span className="animate-pulse">Запуск...</span>
                  ) : (
                    'Запустить'
                  )}
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* History */}
        <div className="md:col-span-2">
          <Card className="border-slate-700 bg-slate-800 shadow-lg">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <History className="h-5 w-5 text-orange-400" />
                История запусков
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {isLoadingHistory ? (
                <div className="flex justify-center items-center h-64">
                  <div className="flex flex-col items-center justify-center space-y-4">
                    <LoadingSpinner className="h-8 w-8 text-blue-500" />
                    <span className="text-slate-400 font-medium">Загрузка истории...</span>
                  </div>
                </div>
              ) : (
                <div className="overflow-x-auto max-h-[500px] scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
                  <table className="min-w-full relative">
                    <thead className="sticky top-0 z-10 bg-gradient-to-r from-slate-700 to-slate-600 shadow-md">
                      <tr>
                        <th className="px-4 py-3 text-left font-bold text-slate-200">Группа</th>
                        <th className="px-4 py-3 text-left font-bold text-slate-200">Статус</th>
                        <th className="px-4 py-3 text-left font-bold text-slate-200">Длительность</th>
                        <th className="px-4 py-3 text-left font-bold text-slate-200">Время</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                      {history?.items?.map((task: ParseTaskResponse, index: number) => (
                        <tr
                          key={task.task_id}
                          className="group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01]"
                          style={{ animationDelay: `${index * 50}ms` }}
                        >
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                                <span className="text-white text-xs font-bold">
                                  {task.group_name?.charAt(0)?.toUpperCase() || 'G'}
                                </span>
                              </div>
                              <span className="text-slate-200 font-medium">{task.group_name}</span>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <ParserStatus status={task.status} />
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <Timer className="h-4 w-4 text-purple-400" />
                              <span className="text-slate-300">
                                {task.stats?.duration_seconds
                                  ? `${task.stats.duration_seconds} сек`
                                  : '-'}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4 text-blue-400" />
                              <span className="text-slate-300">
                                {task.completed_at
                                  ? formatDistanceToNow(new Date(task.completed_at), {
                                    addSuffix: true,
                                    locale: ru,
                                  })
                                  : '-'}
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
