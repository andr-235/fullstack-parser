'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Key } from 'lucide-react'

export function SettingsApi() {
 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Key className="h-5 w-5" />
     Конфигурация VK API
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    <div className="space-y-2">
     <Label htmlFor="vk-token">Токен VK API</Label>
     <Input
      id="vk-token"
      type="password"
      placeholder="Введите ваш токен VK API"
      defaultValue="••••••••••••••••"
     />
    </div>

    <div className="grid gap-4 md:grid-cols-2">
     <div className="space-y-2">
      <Label htmlFor="api-version">Версия API</Label>
      <Select defaultValue="5.199">
       <SelectTrigger>
        <SelectValue />
       </SelectTrigger>
       <SelectContent>
        <SelectItem value="5.199">5.199 (Последняя)</SelectItem>
        <SelectItem value="5.198">5.198</SelectItem>
        <SelectItem value="5.197">5.197</SelectItem>
       </SelectContent>
      </Select>
     </div>
     <div className="space-y-2">
      <Label htmlFor="rate-limit">Лимит запросов (запросов/мин)</Label>
      <Input id="rate-limit" type="number" defaultValue="5" />
     </div>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="api-caching" defaultChecked />
     <Label htmlFor="api-caching">Включить кэширование ответов API</Label>
    </div>

    <Button variant="outline" className="w-fit">
     Протестировать подключение к API
    </Button>
   </CardContent>
  </Card>
 )
}
