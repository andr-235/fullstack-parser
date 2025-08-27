'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Button,
  Input,
  Label,
  Switch,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui'
import type { VKGroupMonitoring, MonitoringGroupUpdate } from '@/shared/types'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { formatDateTimeShort } from '@/shared/lib/time-utils'

interface MonitoringSettingsProps {
  group: VKGroupMonitoring
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: (updateData: MonitoringGroupUpdate) => void
}

export default function MonitoringSettings({
  group,
  open,
  onOpenChange,
  onSave,
}: MonitoringSettingsProps) {
  const [enabled, setEnabled] = useState(group.auto_monitoring_enabled)
  const [intervalMinutes, setIntervalMinutes] = useState(
    group.monitoring_interval_minutes
  )
  const [priority, setPriority] = useState(group.monitoring_priority)

  const handleSave = () => {
    onSave({
      auto_monitoring_enabled: enabled,
      monitoring_interval_minutes: intervalMinutes,
      monitoring_priority: priority,
    })
  }

  const handleCancel = () => {
    // Сбрасываем значения к исходным
    setEnabled(group.auto_monitoring_enabled)
    setIntervalMinutes(group.monitoring_interval_minutes)
    setPriority(group.monitoring_priority)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Настройки мониторинга</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Информация о группе */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Группа</Label>
            <div className="p-3 bg-slate-800 rounded-md">
              <div className="font-medium">
                {group.group_name || group.name}
              </div>
              <div className="text-sm text-slate-400">@{group.screen_name}</div>
            </div>
          </div>

          {/* Включение/отключение мониторинга */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-sm font-medium">
                Автоматический мониторинг
              </Label>
              <p className="text-sm text-slate-400">
                Включить автоматическую проверку группы
              </p>
            </div>
            <Switch checked={enabled} onCheckedChange={setEnabled} />
          </div>

          {/* Интервал мониторинга */}
          <div className="space-y-2">
            <Label htmlFor="interval" className="text-sm font-medium">
              Интервал проверки (минуты)
            </Label>
            <Select
              value={intervalMinutes.toString()}
              onValueChange={(value) => setIntervalMinutes(parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5 минут</SelectItem>
                <SelectItem value="15">15 минут</SelectItem>
                <SelectItem value="30">30 минут</SelectItem>
                <SelectItem value="60">1 час</SelectItem>
                <SelectItem value="120">2 часа</SelectItem>
                <SelectItem value="240">4 часа</SelectItem>
                <SelectItem value="480">8 часов</SelectItem>
                <SelectItem value="1440">1 день</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-400">
              Минимум: 1 минута, максимум: 24 часа (1440 минут)
            </p>
          </div>

          {/* Приоритет мониторинга */}
          <div className="space-y-2">
            <Label htmlFor="priority" className="text-sm font-medium">
              Приоритет мониторинга
            </Label>
            <Select
              value={priority.toString()}
              onValueChange={(value) => setPriority(parseInt(value))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1 - Низкий</SelectItem>
                <SelectItem value="2">2</SelectItem>
                <SelectItem value="3">3</SelectItem>
                <SelectItem value="4">4</SelectItem>
                <SelectItem value="5">5 - Средний</SelectItem>
                <SelectItem value="6">6</SelectItem>
                <SelectItem value="7">7</SelectItem>
                <SelectItem value="8">8</SelectItem>
                <SelectItem value="9">9</SelectItem>
                <SelectItem value="10">10 - Высокий</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-400">
              Группы с высоким приоритетом проверяются первыми
            </p>
          </div>

          {/* Статистика */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Статистика</Label>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-400">Запусков:</span>
                <span className="ml-2 font-medium">
                  {group.monitoring_runs_count}
                </span>
              </div>
              <div>
                <span className="text-slate-400">Последний успех:</span>
                <span className="ml-2 font-medium">
                  {group.last_monitoring_success
                    ? group.last_monitoring_success_local ||
                      formatDateTimeShort(group.last_monitoring_success)
                    : 'Нет'}
                </span>
              </div>
            </div>
          </div>

          {/* Кнопки */}
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={handleCancel}>
              Отмена
            </Button>
            <Button onClick={handleSave}>Сохранить</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
