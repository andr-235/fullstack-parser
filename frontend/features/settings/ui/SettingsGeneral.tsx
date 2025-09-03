'use client'

import { Settings } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'

export function SettingsGeneral() {
 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Settings className="h-5 w-5" />
     Общие настройки
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    <div className="grid gap-4 md:grid-cols-2">
     <div className="space-y-2">
      <Label htmlFor="app-name">Название приложения</Label>
      <Input id="app-name" defaultValue="Парсер комментариев VK" />
     </div>
     <div className="space-y-2">
      <Label htmlFor="app-description">Описание</Label>
      <Input id="app-description" defaultValue="Мониторинг комментариев групп VK" />
     </div>
    </div>

    <div className="space-y-2">
     <Label htmlFor="timezone">Часовой пояс</Label>
     <Select defaultValue="utc">
      <SelectTrigger>
       <SelectValue placeholder="Выберите часовой пояс" />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="utc">UTC</SelectItem>
       <SelectItem value="moscow">Москва (MSK)</SelectItem>
       <SelectItem value="london">Лондон (GMT)</SelectItem>
       <SelectItem value="new-york">Нью-Йорк (EST)</SelectItem>
      </SelectContent>
     </Select>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="auto-refresh" defaultChecked />
     <Label htmlFor="auto-refresh">Включить автообновление</Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="debug-mode" />
     <Label htmlFor="debug-mode">Режим отладки</Label>
    </div>
   </CardContent>
  </Card>
 )
}
