/**
 * Таб настроек VK API
 */

'use client'

import { useState } from 'react'
import {
  useSettings,
  useUpdateSettings,
  useTestVKAPIConnection,
} from '../hooks'
import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Wifi, Eye, EyeOff, TestTube } from 'lucide-react'
import { SETTINGS_VALIDATION } from '@/types/settings'

export function VKAPISettingsTab() {
  const { data: settingsData, isLoading } = useSettings()
  const updateSettings = useUpdateSettings()
  const testConnection = useTestVKAPIConnection()

  const [showToken, setShowToken] = useState(false)
  const [formData, setFormData] = useState({
    access_token: '',
    api_version: '5.131',
    requests_per_second: 3,
  })

  // Инициализируем форму при загрузке данных
  if (settingsData && !isLoading && formData.access_token === '') {
    setFormData({
      access_token: settingsData.settings.vk_api.access_token,
      api_version: settingsData.settings.vk_api.api_version,
      requests_per_second: settingsData.settings.vk_api.requests_per_second,
    })
  }

  const handleInputChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    await updateSettings.mutateAsync({
      vk_api: formData,
    })
  }

  const handleTestConnection = async () => {
    await testConnection.mutateAsync({
      accessToken: formData.access_token,
      apiVersion: formData.api_version,
    })
  }

  const isTokenValid = formData.access_token.length > 0
  const isRequestsValid =
    formData.requests_per_second >=
    SETTINGS_VALIDATION.vk_api.requests_per_second.min &&
    formData.requests_per_second <=
    SETTINGS_VALIDATION.vk_api.requests_per_second.max

  if (isLoading) {
    return <div>Загрузка настроек...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold">Настройки VK API</h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Конфигурация для работы с API ВКонтакте
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wifi className="h-5 w-5" />
            Параметры подключения
          </CardTitle>
          <CardDescription>
            Настройте токен доступа и параметры API ВКонтакте
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Access Token */}
          <div className="space-y-2">
            <Label htmlFor="access_token" className="flex items-center gap-2">
              Access Token
              <Badge variant={isTokenValid ? 'default' : 'destructive'}>
                {isTokenValid ? 'Установлен' : 'Не установлен'}
              </Badge>
            </Label>
            <div className="relative">
              <Input
                id="access_token"
                type={showToken ? 'text' : 'password'}
                value={formData.access_token}
                onChange={(e) =>
                  handleInputChange('access_token', e.target.value)
                }
                placeholder="Введите VK Access Token"
                className="pr-10"
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-slate-500">
              Токен доступа для работы с API ВКонтакте
            </p>
          </div>

          {/* API Version */}
          <div className="space-y-2">
            <Label htmlFor="api_version">Версия API</Label>
            <Input
              id="api_version"
              value={formData.api_version}
              onChange={(e) => handleInputChange('api_version', e.target.value)}
              placeholder="5.131"
            />
            <p className="text-xs text-slate-500">
              Версия API ВКонтакте (рекомендуется 5.131)
            </p>
          </div>

          {/* Requests per Second */}
          <div className="space-y-2">
            <Label
              htmlFor="requests_per_second"
              className="flex items-center gap-2"
            >
              Запросов в секунду
              <Badge variant={isRequestsValid ? 'default' : 'destructive'}>
                {isRequestsValid ? 'Валидно' : 'Недопустимо'}
              </Badge>
            </Label>
            <Input
              id="requests_per_second"
              type="number"
              min={SETTINGS_VALIDATION.vk_api.requests_per_second.min}
              max={SETTINGS_VALIDATION.vk_api.requests_per_second.max}
              value={formData.requests_per_second}
              onChange={(e) =>
                handleInputChange(
                  'requests_per_second',
                  parseInt(e.target.value) || 3
                )
              }
            />
            <p className="text-xs text-slate-500">
              Лимит запросов в секунду (от{' '}
              {SETTINGS_VALIDATION.vk_api.requests_per_second.min} до{' '}
              {SETTINGS_VALIDATION.vk_api.requests_per_second.max})
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleSave}
              disabled={
                updateSettings.isPending || !isTokenValid || !isRequestsValid
              }
            >
              {updateSettings.isPending ? 'Сохранение...' : 'Сохранить'}
            </Button>

            <Button
              variant="outline"
              onClick={handleTestConnection}
              disabled={testConnection.isPending || !isTokenValid}
            >
              <TestTube className="h-4 w-4 mr-2" />
              {testConnection.isPending
                ? 'Тестирование...'
                : 'Тест подключения'}
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
            <p>
              • Access Token можно получить в настройках приложения ВКонтакте
            </p>
            <p>• Рекомендуется использовать версию API 5.131</p>
            <p>• Лимит запросов зависит от типа токена и настроек приложения</p>
            <p>• Используйте тест подключения для проверки работоспособности</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
