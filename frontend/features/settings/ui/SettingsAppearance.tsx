'use client'

import { Palette } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'

export function SettingsAppearance() {
 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Palette className="h-5 w-5" />
     Настройки внешнего вида
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    <div className="space-y-2">
     <Label htmlFor="theme">Тема</Label>
     <Select defaultValue="dark">
      <SelectTrigger>
       <SelectValue />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="light">Светлая</SelectItem>
       <SelectItem value="dark">Темная</SelectItem>
       <SelectItem value="system">Системная</SelectItem>
      </SelectContent>
     </Select>
    </div>

    <div className="space-y-2">
     <Label htmlFor="language">Язык</Label>
     <Select defaultValue="ru">
      <SelectTrigger>
       <SelectValue />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="ru">Русский</SelectItem>
       <SelectItem value="en">English</SelectItem>
       <SelectItem value="es">Español</SelectItem>
      </SelectContent>
     </Select>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="animations" defaultChecked />
     <Label htmlFor="animations">Включить анимации</Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch id="compact-mode" />
     <Label htmlFor="compact-mode">Компактный режим</Label>
    </div>

    <div className="space-y-2">
     <Label htmlFor="items-per-page">Элементов на страницу</Label>
     <Select defaultValue="20">
      <SelectTrigger>
       <SelectValue />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="10">10</SelectItem>
       <SelectItem value="20">20</SelectItem>
       <SelectItem value="50">50</SelectItem>
       <SelectItem value="100">100</SelectItem>
      </SelectContent>
     </Select>
    </div>
   </CardContent>
  </Card>
 )
}
