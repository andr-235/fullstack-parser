/**
 * Таб настроек мониторинга
 */

'use client'

import { useState } from 'react'
import { useSettings, useUpdateSettings } from '@/hooks/use-settings'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Clock, Users, Timer, Play } from 'lucide-react'
import { SETTINGS_VALIDATION } from '@/types/settings'

export function MonitoringSettingsTab() {
  const { data: settingsData, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()

  const [formData, setFormData] = useState({
    scheduler_interval_seconds: 300,
    max_concurrent_groups: 10,
    group_delay_seconds: 1,
    auto_start_scheduler: false,
  })

  // Инициализируем форму при загрузке данных
  if (
    settingsData &&
    !isLoading &&
    formData.scheduler_interval_seconds === 300
  ) {
    setFormData({
      scheduler_interval_seconds:
        settingsData.settings.monitoring.scheduler_interval_seconds,
      max_concurrent_groups:
        settingsData.settings.monitoring.max_concurrent_groups,
      group_delay_seconds: settingsData.settings.monitoring.group_delay_seconds,
      auto_start_scheduler:
        settingsData.settings.monitoring.auto_start_scheduler,
    })
  }

  const handleInputChange = (
    field: string,
    value: string | number | boolean
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    await updateSettings.mutateAsync({
      monitoring: formData,
    })
  }

  const isIntervalValid =
    formData.scheduler_interval_seconds >=
      SETTINGS_VALIDATION.monitoring.scheduler_interval_seconds.min &&
    formData.scheduler_interval_seconds <=
      SETTINGS_VALIDATION.monitoring.scheduler_interval_seconds.max

  const isGroupsValid =
    formData.max_concurrent_groups >=
      SETTINGS_VALIDATION.monitoring.max_concurrent_groups.min &&
    formData.max_concurrent_groups <=
      SETTINGS_VALIDATION.monitoring.max_concurrent_groups.max

  const isDelayValid =
    formData.group_delay_seconds >=
      SETTINGS_VALIDATION.monitoring.group_delay_seconds.min &&
    formData.group_delay_seconds <=
      SETTINGS_VALIDATION.monitoring.group_delay_seconds.max

  if (isLoading) {
    return <div>Загрузка настроек...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Настройки мониторинга</h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Конфигурация автоматического мониторинга групп ВКонтакте
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Планировщик
          </CardTitle>
          <CardDescription>
            Настройте интервалы и параметры автоматического мониторинга
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Интервал планировщика */}
          <div className="space-y-2">
            <Label
              htmlFor="scheduler_interval"
              className="flex items-center gap-2"
            >
              Интервал планировщика (секунды)
              <Badge variant={isIntervalValid ? 'default' : 'destructive'}>
                {isIntervalValid ? 'Валидно' : 'Недопустимо'}
              </Badge>
            </Label>
            <Input
              id="scheduler_interval"
              type="number"
              min={
                SETTINGS_VALIDATION.monitoring.scheduler_interval_seconds.min
              }
              max={
                SETTINGS_VALIDATION.monitoring.scheduler_interval_seconds.max
              }
              value={formData.scheduler_interval_seconds}
              onChange={(e) =>
                handleInputChange(
                  'scheduler_interval_seconds',
                  parseInt(e.target.value) || 300
                )
              }
            />
            <p className="text-xs text-slate-500">
              Как часто запускать цикл мониторинга (от{' '}
              {SETTINGS_VALIDATION.monitoring.scheduler_interval_seconds.min} до{' '}
              {SETTINGS_VALIDATION.monitoring.scheduler_interval_seconds.max}{' '}
              сек)
            </p>
          </div>

          {/* Максимум групп */}
          <div className="space-y-2">
            <Label htmlFor="max_groups" className="flex items-center gap-2">
              Максимум групп одновременно
              <Badge variant={isGroupsValid ? 'default' : 'destructive'}>
                {isGroupsValid ? 'Валидно' : 'Недопустимо'}
              </Badge>
            </Label>
            <Input
              id="max_groups"
              type="number"
              min={SETTINGS_VALIDATION.monitoring.max_concurrent_groups.min}
              max={SETTINGS_VALIDATION.monitoring.max_concurrent_groups.max}
              value={formData.max_concurrent_groups}
              onChange={(e) =>
                handleInputChange(
                  'max_concurrent_groups',
                  parseInt(e.target.value) || 10
                )
              }
            />
            <p className="text-xs text-slate-500">
              Максимальное количество групп для одновременного мониторинга
            </p>
          </div>

          {/* Задержка между группами */}
          <div className="space-y-2">
            <Label htmlFor="group_delay" className="flex items-center gap-2">
              Задержка между группами (секунды)
              <Badge variant={isDelayValid ? 'default' : 'destructive'}>
                {isDelayValid ? 'Валидно' : 'Недопустимо'}
              </Badge>
            </Label>
            <Input
              id="group_delay"
              type="number"
              min={SETTINGS_VALIDATION.monitoring.group_delay_seconds.min}
              max={SETTINGS_VALIDATION.monitoring.group_delay_seconds.max}
              value={formData.group_delay_seconds}
              onChange={(e) =>
                handleInputChange(
                  'group_delay_seconds',
                  parseInt(e.target.value) || 1
                )
              }
            />
            <p className="text-xs text-slate-500">
              Пауза между мониторингом разных групп для избежания лимитов
            </p>
          </div>

          {/* Автозапуск планировщика */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="auto_start">Автозапуск планировщика</Label>
              <p className="text-xs text-slate-500">
                Автоматически запускать планировщик при старте приложения
              </p>
            </div>
            <Switch
              id="auto_start"
              checked={formData.auto_start_scheduler}
              onCheckedChange={(checked) =>
                handleInputChange('auto_start_scheduler', checked)
              }
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleSave}
              disabled={
                updateSettings.isPending ||
                !isIntervalValid ||
                !isGroupsValid ||
                !isDelayValid
              }
            >
              {updateSettings.isPending ? 'Сохранение...' : 'Сохранить'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Информация */}
      <Card>
        <CardHeader>
          <CardTitle>Информация</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <p>• Интервал планировщика определяет частоту проверки групп</p>
            <p>• Максимум групп влияет на нагрузку на систему и VK API</p>
            <p>• Задержка между группами помогает избежать лимитов API</p>
            <p>• Автозапуск удобен для production окружения</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
