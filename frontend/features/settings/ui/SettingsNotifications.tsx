'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Separator } from '@/shared/ui'
import { Bell } from 'lucide-react'

export function SettingsNotifications() {
 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Bell className="h-5 w-5" />
     Настройки уведомлений
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    <div className="flex items-center space-x-2">
     <Switch id="email-notifications" defaultChecked />
     <Label htmlFor="email-notifications">Уведомления по email</Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="push-notifications" />
     <Label htmlFor="push-notifications">Push-уведомления</Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="keyword-alerts" defaultChecked />
     <Label htmlFor="keyword-alerts">Уведомления о совпадениях ключевых слов</Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="error-alerts" defaultChecked />
     <Label htmlFor="error-alerts">Уведомления об ошибках</Label>
    </div>

    <Separator />

    <div className="space-y-2">
     <Label htmlFor="email-address">Email адрес</Label>
     <Input id="email-address" type="email" placeholder="admin@example.com" />
    </div>

    <div className="space-y-2">
     <Label htmlFor="notification-frequency">Частота уведомлений</Label>
     <Select defaultValue="immediate">
      <SelectTrigger>
       <SelectValue />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="immediate">Немедленно</SelectItem>
       <SelectItem value="hourly">Почасовой дайджест</SelectItem>
       <SelectItem value="daily">Ежедневный дайджест</SelectItem>
      </SelectContent>
     </Select>
    </div>
   </CardContent>
  </Card>
 )
}
