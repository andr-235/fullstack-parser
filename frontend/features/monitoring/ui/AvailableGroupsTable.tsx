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
} from '@/shared/ui'
import { useEnableGroupMonitoring, useRunGroupMonitoring } from '../hooks'

import { Play, Settings, Plus, Clock } from 'lucide-react'

import type { VKGroupMonitoring } from '@/types/api'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { formatDateTimeShort } from '@/shared/lib/time-utils'
import MonitoringSettings from './MonitoringSettings'

interface AvailableGroupsTableProps {
  groups: VKGroupMonitoring[]
}

export default function AvailableGroupsTable({
  groups,
}: AvailableGroupsTableProps) {
  const [settingsGroup, setSettingsGroup] = useState<VKGroupMonitoring | null>(
    null
  )
  const [showSettings, setShowSettings] = useState(false)

  const enableMutation = useEnableGroupMonitoring()
  const runMutation = useRunGroupMonitoring()

  const handleEnableMonitoring = (group: VKGroupMonitoring) => {
    // Используем setTimeout чтобы избежать setState во время рендеринга
    setTimeout(() => {
      enableMutation.mutate({
        groupId: group.id,
        intervalMinutes: group.monitoring_interval_minutes,
        priority: group.monitoring_priority,
      })
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

  const getLastActivityTime = (group: VKGroupMonitoring) => {
    if (group.last_monitoring_success) {
      const displayTime =
        group.last_monitoring_success_local ||
        formatDateTimeShort(group.last_monitoring_success)
      return `Последний запуск: ${displayTime}`
    }
    return 'Никогда не запускался'
  }

  if (groups.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-400">Нет групп, доступных для мониторинга</p>
        <p className="text-sm text-slate-500 mt-2">
          Добавьте группы в разделе "Группы" для начала мониторинга
        </p>
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
              <TableHead>Последняя активность</TableHead>
              <TableHead>Запусков</TableHead>
              <TableHead className="text-right">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {groups.map((group, index) => (
              <TableRow key={group.id || `available-group-${index}`}>
                <TableCell>
                  <div>
                    <div className="font-medium">{group.name}</div>
                    <div className="text-sm text-slate-400">
                      @{group.screen_name}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="secondary" className="bg-slate-600">
                    <Clock className="h-3 w-3 mr-1" />
                    Доступна
                  </Badge>
                </TableCell>
                <TableCell>
                  <span className="text-sm text-slate-400">
                    {getLastActivityTime(group)}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="text-sm">
                    {group.monitoring_runs_count || 0}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center gap-2 justify-end">
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
                    <Button
                      size="sm"
                      onClick={() => handleEnableMonitoring(group)}
                      disabled={enableMutation.isPending}
                      className="flex items-center gap-1"
                    >
                      <Plus className="h-3 w-3" />
                      {enableMutation.isPending ? 'Включение...' : 'Включить'}
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
              enableMutation.mutate({
                groupId: settingsGroup.id,
                intervalMinutes: updateData.monitoring_interval_minutes || 15,
                priority: updateData.monitoring_priority || 1,
              })
              setShowSettings(false)
            }, 0)
          }}
        />
      )}
    </>
  )
}
