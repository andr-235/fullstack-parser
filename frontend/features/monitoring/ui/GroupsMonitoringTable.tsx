'use client'

import { useState } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Button,
  Badge,
  Switch,
  Progress,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/shared/ui'
import {
  useEnableGroupMonitoring,
  useDisableGroupMonitoring,
  useRunGroupMonitoring,
  useUpdateGroupMonitoring,
} from '../hooks'
import {
  Play,
  Settings,
  Clock,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Timer,
  TrendingUp,
  AlertCircle,
  Activity,
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  formatDateTimeShort,
  isOverdue,
  calculateProgress,
  formatNextRunTime,
} from '@/shared/lib/time-utils'
import type { VKGroupMonitoring } from '@/types/api'
import MonitoringSettings from './MonitoringSettings'

interface GroupsMonitoringTableProps {
  groups: VKGroupMonitoring[]
}

export default function GroupsMonitoringTable({
  groups,
}: GroupsMonitoringTableProps) {
  const [settingsGroup, setSettingsGroup] = useState<VKGroupMonitoring | null>(
    null
  )
  const [showSettings, setShowSettings] = useState(false)

  const enableMutation = useEnableGroupMonitoring()
  const disableMutation = useDisableGroupMonitoring()
  const runMutation = useRunGroupMonitoring()
  const updateMutation = useUpdateGroupMonitoring()

  const handleToggleMonitoring = (group: VKGroupMonitoring) => {
    setTimeout(() => {
      if (group.auto_monitoring_enabled) {
        disableMutation.mutate(group.id)
      } else {
        enableMutation.mutate({
          groupId: group.id,
          intervalMinutes: 60,
          priority: 5,
        })
      }
    }, 0)
  }

  const handleRunMonitoring = (groupId: number) => {
    setTimeout(() => {
      runMutation.mutate(groupId)
    }, 0)
  }

  const handleOpenSettings = (group: VKGroupMonitoring) => {
    setTimeout(() => {
      setSettingsGroup(group)
      setShowSettings(true)
    }, 0)
  }

  const getStatusIcon = (group: VKGroupMonitoring) => {
    if (!group.auto_monitoring_enabled) {
      return <XCircle className="h-4 w-4 text-slate-400" />
    }

    if (group.last_monitoring_error) {
      return <AlertTriangle className="h-4 w-4 text-red-400" />
    }

    if (group.last_monitoring_success) {
      return <CheckCircle className="h-4 w-4 text-green-400" />
    }

    return <Clock className="h-4 w-4 text-yellow-400" />
  }

  const getStatusText = (group: VKGroupMonitoring) => {
    if (!group.auto_monitoring_enabled) {
      return 'Отключен'
    }

    if (group.last_monitoring_error) {
      return 'Ошибка'
    }

    if (group.last_monitoring_success) {
      return 'Работает'
    }

    return 'Ожидает'
  }

  const getStatusColor = (group: VKGroupMonitoring) => {
    if (!group.auto_monitoring_enabled) {
      return 'text-slate-400'
    }

    if (group.last_monitoring_error) {
      return 'text-red-400'
    }

    if (group.last_monitoring_success) {
      return 'text-green-400'
    }

    return 'text-yellow-400'
  }

  const getNextMonitoringTime = (group: VKGroupMonitoring) => {
    if (!group.next_monitoring_at || group.next_monitoring_at === 'null') {
      return {
        text: 'Не запланировано',
        progress: 0,
        status: 'waiting',
        color: 'text-slate-400',
      }
    }

    // Вычисляем прогресс для интервала мониторинга
    const progress = calculateProgress(
      group.next_monitoring_at,
      group.monitoring_interval_minutes || 60
    )

    // Используем локальное время, которое уже приходит с сервера
    const displayText =
      group.next_monitoring_at_local ||
      formatNextRunTime(group.next_monitoring_at)

    return {
      text: displayText,
      progress,
      status: 'running',
      color: 'text-blue-400',
    }
  }

  const getLastMonitoringTime = (group: VKGroupMonitoring) => {
    if (group.last_monitoring_success) {
      const displayTime =
        group.last_monitoring_success_local ||
        formatDateTimeShort(group.last_monitoring_success)
      return {
        text: displayTime,
        status: 'success',
        color: 'text-green-400',
      }
    }

    if (group.last_monitoring_error) {
      return {
        text: 'Ошибка',
        status: 'error',
        color: 'text-red-400',
      }
    }

    return {
      text: 'Никогда',
      status: 'never',
      color: 'text-slate-400',
    }
  }

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'bg-red-600 text-white'
    if (priority >= 6) return 'bg-orange-600 text-white'
    if (priority >= 4) return 'bg-yellow-600 text-white'
    return 'bg-blue-600 text-white'
  }

  const getIntervalColor = (minutes: number) => {
    if (minutes <= 30) return 'text-red-400'
    if (minutes <= 60) return 'text-orange-400'
    if (minutes <= 120) return 'text-yellow-400'
    return 'text-green-400'
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-slate-700 rounded-full">
            <Activity className="h-8 w-8 text-slate-400" />
          </div>
          <div>
            <p className="text-slate-400 font-medium">
              Нет групп с мониторингом
            </p>
            <p className="text-sm text-slate-500 mt-1">
              Добавьте группы в мониторинг для автоматической проверки
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <TooltipProvider>
      <div className="rounded-md border border-slate-700">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Группа</TableHead>
              <TableHead>Статус</TableHead>
              <TableHead>Приоритет</TableHead>
              <TableHead>Интервал</TableHead>
              <TableHead>Последний запуск</TableHead>
              <TableHead>Следующий запуск</TableHead>
              <TableHead>Запусков</TableHead>
              <TableHead className="text-right">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {groups.map((group, index) => {
              const nextMonitoring = getNextMonitoringTime(group)
              const lastMonitoring = getLastMonitoringTime(group)

              return (
                <TableRow
                  key={group.id || `group-${index}`}
                  className="hover:bg-slate-700/50"
                >
                  <TableCell>
                    <div>
                      <div className="font-medium">{group.name}</div>
                      <div className="text-sm text-slate-400">
                        @{group.screen_name}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(group)}
                      <span className={`text-sm ${getStatusColor(group)}`}>
                        {getStatusText(group)}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="inline-block">
                      <Tooltip>
                        <TooltipTrigger>
                          <Badge
                            className={getPriorityColor(
                              group.monitoring_priority
                            )}
                          >
                            {group.monitoring_priority}/10
                          </Badge>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Приоритет мониторинга группы</p>
                          <p className="text-xs text-slate-300">
                            {group.monitoring_priority >= 8
                              ? 'Критический'
                              : group.monitoring_priority >= 6
                                ? 'Высокий'
                                : group.monitoring_priority >= 4
                                  ? 'Средний'
                                  : 'Низкий'}
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="inline-block">
                      <Tooltip>
                        <TooltipTrigger>
                          <span
                            className={`text-sm ${getIntervalColor(group.monitoring_interval_minutes)}`}
                          >
                            {group.monitoring_interval_minutes} мин
                          </span>
                        </TooltipTrigger>
                        <TooltipContent>
                          <p>Интервал проверки группы</p>
                          <p className="text-xs text-slate-300">
                            {group.monitoring_interval_minutes <= 30
                              ? 'Очень часто'
                              : group.monitoring_interval_minutes <= 60
                                ? 'Часто'
                                : group.monitoring_interval_minutes <= 120
                                  ? 'Умеренно'
                                  : 'Редко'}
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm ${lastMonitoring.color}`}>
                        {lastMonitoring.text}
                      </span>
                      {lastMonitoring.status === 'success' && (
                        <CheckCircle className="h-3 w-3 text-green-400" />
                      )}
                      {lastMonitoring.status === 'error' && (
                        <AlertCircle className="h-3 w-3 text-red-400" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      <span className={`text-sm ${nextMonitoring.color}`}>
                        {nextMonitoring.text}
                      </span>
                      {nextMonitoring.status === 'running' && (
                        <Progress
                          value={nextMonitoring.progress}
                          className="h-1"
                        />
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className="text-sm">
                        {group.monitoring_runs_count}
                      </span>
                      {group.monitoring_runs_count > 0 && (
                        <TrendingUp className="h-3 w-3 text-green-400" />
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center gap-2 justify-end">
                      <div className="inline-block">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Switch
                              checked={group.auto_monitoring_enabled}
                              onCheckedChange={() =>
                                handleToggleMonitoring(group)
                              }
                              disabled={
                                enableMutation.isPending ||
                                disableMutation.isPending
                              }
                            />
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>
                              {group.auto_monitoring_enabled
                                ? 'Отключить'
                                : 'Включить'}{' '}
                              мониторинг
                            </p>
                          </TooltipContent>
                        </Tooltip>
                      </div>

                      <div className="inline-block">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleRunMonitoring(group.id)}
                              disabled={runMutation.isPending}
                            >
                              <Play className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Запустить мониторинг сейчас</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>

                      <div className="inline-block">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleOpenSettings(group)}
                            >
                              <Settings className="h-3 w-3" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>Настройки мониторинга</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </div>

      {/* Модальное окно настроек */}
      {showSettings && settingsGroup && (
        <MonitoringSettings
          group={settingsGroup}
          open={showSettings}
          onOpenChange={setShowSettings}
          onSave={(updateData) => {
            updateMutation.mutate({
              groupId: settingsGroup.id,
              updateData,
            })
            setShowSettings(false)
          }}
        />
      )}
    </TooltipProvider>
  )
}
