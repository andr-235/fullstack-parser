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
} from '@/shared/ui'
import {
  useEnableGroupMonitoring,
  useDisableGroupMonitoring,
  useRunGroupMonitoring,
  useUpdateGroupMonitoring,
} from '@/hooks/use-monitoring'
import {
  Play,
  Settings,
  Clock,
  CheckCircle,
  AlertTriangle,
  XCircle,
} from 'lucide-react'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
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
    // Используем setTimeout чтобы избежать setState во время рендеринга
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
    // Используем setTimeout чтобы избежать setState во время рендеринга
    setTimeout(() => {
      runMutation.mutate(groupId)
    }, 0)
  }

  const handleOpenSettings = (group: VKGroupMonitoring) => {
    // Используем setTimeout чтобы избежать setState во время рендеринга
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

  const getNextMonitoringTime = (group: VKGroupMonitoring) => {
    if (!group.next_monitoring_at || group.next_monitoring_at === 'null') {
      return 'Не запланировано'
    }

    const nextTime = new Date(group.next_monitoring_at)
    const now = new Date()

    // Если время в прошлом, показываем "Просрочено"
    if (nextTime < now) {
      return 'Просрочено'
    }

    return formatDistanceToNow(nextTime, {
      addSuffix: true,
      locale: ru,
    })
  }

  const getLastMonitoringTime = (group: VKGroupMonitoring) => {
    if (group.last_monitoring_success) {
      return formatDistanceToNow(new Date(group.last_monitoring_success), {
        addSuffix: true,
        locale: ru,
      })
    }

    if (group.last_monitoring_error) {
      return 'Ошибка'
    }

    return 'Никогда'
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-400">Нет групп с мониторингом</p>
      </div>
    )
  }

  return (
    <>
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
            {groups.map((group, index) => (
              <TableRow key={group.id || `group-${index}`}>
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
                    <span className="text-sm">{getStatusText(group)}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">
                    {group.monitoring_priority}/10
                  </Badge>
                </TableCell>
                <TableCell>
                  <span className="text-sm">
                    {group.monitoring_interval_minutes} мин
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-sm text-slate-400">
                    {getLastMonitoringTime(group)}
                  </span>
                </TableCell>
                <TableCell>
                  <span
                    className={`text-sm ${
                      getNextMonitoringTime(group) === 'Просрочено'
                        ? 'text-red-400'
                        : getNextMonitoringTime(group) === 'Не запланировано'
                          ? 'text-slate-400'
                          : 'text-slate-400'
                    }`}
                  >
                    {getNextMonitoringTime(group)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-sm">{group.monitoring_runs_count}</span>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center gap-2 justify-end">
                    <Switch
                      checked={group.auto_monitoring_enabled}
                      onCheckedChange={() => handleToggleMonitoring(group)}
                      disabled={
                        enableMutation.isPending || disableMutation.isPending
                      }
                    />
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRunMonitoring(group.id)}
                      disabled={runMutation.isPending}
                    >
                      <Play className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleOpenSettings(group)}
                    >
                      <Settings className="h-3 w-3" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
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
            // Используем setTimeout чтобы избежать setState во время рендеринга
            setTimeout(() => {
              updateMutation.mutate({
                groupId: settingsGroup.id,
                updateData,
              })
              setShowSettings(false)
            }, 0)
          }}
        />
      )}
    </>
  )
}
