'use client'

import { Database } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'

export function SettingsDatabase() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Конфигурация базы данных
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="db-host">Хост базы данных</Label>
            <Input id="db-host" defaultValue="localhost" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="db-port">Порт</Label>
            <Input id="db-port" type="number" defaultValue="5432" />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="db-name">Имя базы данных</Label>
            <Input id="db-name" defaultValue="vk_parser" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="db-user">Имя пользователя</Label>
            <Input id="db-user" defaultValue="postgres" />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="db-password">Пароль</Label>
          <Input id="db-password" type="password" defaultValue="••••••••" />
        </div>

        <div className="flex items-center space-x-2">
          <Switch id="db-ssl" defaultChecked />
          <Label htmlFor="db-ssl">Использовать SSL соединение</Label>
        </div>

        <div className="space-y-2">
          <Label htmlFor="backup-frequency">Частота резервного копирования</Label>
          <Select defaultValue="daily">
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hourly">Каждый час</SelectItem>
              <SelectItem value="daily">Ежедневно</SelectItem>
              <SelectItem value="weekly">Еженедельно</SelectItem>
              <SelectItem value="monthly">Ежемесячно</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  )
}
