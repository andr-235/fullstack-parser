/**
 * Таб настроек логирования
 */

'use client'

import { useState } from 'react'
import { useSettings, useUpdateSettings } from '@/hooks/use-settings'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { FileText } from 'lucide-react'
import { LOG_LEVEL_OPTIONS, LOG_FORMAT_OPTIONS } from '@/types/settings'

export function LoggingSettingsTab() {
  const { data: settingsData, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()

  const [formData, setFormData] = useState({
    level: 'INFO',
    format: 'json',
    include_timestamp: true,
  })

  if (settingsData && !isLoading && formData.level === 'INFO') {
    setFormData({
      level: settingsData.settings.logging.level,
      format: settingsData.settings.logging.format,
      include_timestamp: settingsData.settings.logging.include_timestamp,
    })
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    await updateSettings.mutateAsync({ logging: formData })
  }

  if (isLoading) return <div>Загрузка настроек...</div>

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Настройки логирования</h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Конфигурация системы логирования приложения
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Параметры логирования
          </CardTitle>
          <CardDescription>
            Настройте уровень, формат и параметры логирования
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="log_level">Уровень логирования</Label>
            <Select
              value={formData.level}
              onValueChange={(value) => handleInputChange('level', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Выберите уровень" />
              </SelectTrigger>
              <SelectContent>
                {LOG_LEVEL_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500">
              Минимальный уровень сообщений для записи в лог
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="log_format">Формат логов</Label>
            <Select
              value={formData.format}
              onValueChange={(value) => handleInputChange('format', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Выберите формат" />
              </SelectTrigger>
              <SelectContent>
                {LOG_FORMAT_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-slate-500">
              Формат вывода логов (JSON рекомендуется для production)
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="include_timestamp">
                Включать временные метки
              </Label>
              <p className="text-xs text-slate-500">
                Добавлять временные метки к каждому сообщению
              </p>
            </div>
            <Switch
              id="include_timestamp"
              checked={formData.include_timestamp}
              onCheckedChange={(checked) =>
                handleInputChange('include_timestamp', checked)
              }
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button onClick={handleSave} disabled={updateSettings.isPending}>
              {updateSettings.isPending ? 'Сохранение...' : 'Сохранить'}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
