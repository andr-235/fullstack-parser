'use client'

import { Settings } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

import { SettingsCard } from './SettingsCard'

interface SettingsItem {
  id: string
  title: string
  description: string
  category: 'general' | 'api' | 'database' | 'notifications' | 'appearance'
  status: 'active' | 'inactive' | 'warning' | 'info'
  lastModified: string
  icon: any
}

interface SettingsListProps {
  settings?: SettingsItem[]
  loading?: boolean
}

export function SettingsList({ settings, loading }: SettingsListProps) {
  const mockSettings: SettingsItem[] = [
    {
      id: 'app-name',
      title: 'Название приложения',
      description: 'Парсер комментариев VK',
      category: 'general',
      status: 'active',
      lastModified: '2 часа назад',
      icon: Settings,
    },
    {
      id: 'vk-api',
      title: 'VK API Конфигурация',
      description: 'Токен настроен, версия 5.199',
      category: 'api',
      status: 'active',
      lastModified: '1 день назад',
      icon: Settings,
    },
    {
      id: 'database',
      title: 'База данных',
      description: 'PostgreSQL, SSL включен',
      category: 'database',
      status: 'active',
      lastModified: '3 дня назад',
      icon: Settings,
    },
    {
      id: 'notifications',
      title: 'Уведомления',
      description: 'Email включены, Push отключены',
      category: 'notifications',
      status: 'warning',
      lastModified: '5 часов назад',
      icon: Settings,
    },
    {
      id: 'theme',
      title: 'Тема интерфейса',
      description: 'Темная тема',
      category: 'appearance',
      status: 'active',
      lastModified: '1 неделя назад',
      icon: Settings,
    },
  ]

  const displaySettings = settings || mockSettings

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Настройки системы
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex items-start gap-3 p-4 rounded-lg border">
                <div className="h-10 w-10 bg-gray-200 rounded animate-pulse"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded animate-pulse w-48"></div>
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-32"></div>
                  <div className="h-3 bg-gray-200 rounded animate-pulse w-24"></div>
                </div>
                <div className="h-6 w-16 bg-gray-200 rounded animate-pulse"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (displaySettings.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Настройки системы
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Settings className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Настройки не найдены</p>
            <p className="text-sm text-muted-foreground">
              Настройки системы будут отображаться здесь
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'general':
        return 'Общие'
      case 'api':
        return 'API'
      case 'database':
        return 'База данных'
      case 'notifications':
        return 'Уведомления'
      case 'appearance':
        return 'Внешний вид'
      default:
        return category
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'general':
        return 'bg-blue-500'
      case 'api':
        return 'bg-green-500'
      case 'database':
        return 'bg-purple-500'
      case 'notifications':
        return 'bg-orange-500'
      case 'appearance':
        return 'bg-pink-500'
      default:
        return 'bg-gray-500'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Настройки системы
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {displaySettings.map(setting => (
            <SettingsCard
              key={setting.id}
              title={setting.title}
              description={setting.description}
              status={setting.status}
              badge={getCategoryLabel(setting.category)}
              icon={setting.icon}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
