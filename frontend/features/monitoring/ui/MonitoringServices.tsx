'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

export function MonitoringServices() {
 return (
  <Card>
   <CardHeader>
    <CardTitle>Статус служб</CardTitle>
   </CardHeader>
   <CardContent className="space-y-3">
    <div className="flex items-center justify-between">
     <span className="text-sm">Служба VK API</span>
     <Badge variant="default">Онлайн</Badge>
    </div>
    <div className="flex items-center justify-between">
     <span className="text-sm">База данных</span>
     <Badge variant="default">Онлайн</Badge>
    </div>
    <div className="flex items-center justify-between">
     <span className="text-sm">Парсер комментариев</span>
     <Badge variant="default">Работает</Badge>
    </div>
    <div className="flex items-center justify-between">
     <span className="text-sm">Планировщик</span>
     <Badge variant="secondary">Ожидание</Badge>
    </div>
    <div className="flex items-center justify-between">
     <span className="text-sm">Служба кэша</span>
     <Badge variant="destructive">Офлайн</Badge>
    </div>
   </CardContent>
  </Card>
 )
}
