/**
 * Таб настроек пользовательского интерфейса
 */

'use client'

import { useState } from 'react'
import { useSettings, useUpdateSettings } from '@/hooks/use-settings'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Monitor, RefreshCw, Bell } from 'lucide-react'
import { THEME_OPTIONS, SETTINGS_VALIDATION } from '@/types/settings'

export function UISettingsTab() {
 const { data: settingsData, isLoading } = useSettings()
 const updateSettings = useUpdateSettings()

 const [formData, setFormData] = useState<{
  theme: 'light' | 'dark' | 'system'
  auto_refresh: boolean
  refresh_interval: number
  items_per_page: number
  show_notifications: boolean
 }>({
  theme: 'system',
  auto_refresh: true,
  refresh_interval: 30,
  items_per_page: 20,
  show_notifications: true,
 })

 if (settingsData && !isLoading && formData.theme === 'system') {
  setFormData({
   theme: settingsData.settings.ui.theme,
   auto_refresh: settingsData.settings.ui.auto_refresh,
   refresh_interval: settingsData.settings.ui.refresh_interval,
   items_per_page: settingsData.settings.ui.items_per_page,
   show_notifications: settingsData.settings.ui.show_notifications,
  })
 }

 const handleInputChange = (field: string, value: string | number | boolean) => {
  setFormData(prev => ({ 
   ...prev, 
   [field]: field === 'theme' ? (value as 'light' | 'dark' | 'system') : value 
  }))
 }

 const handleSave = async () => {
  await updateSettings.mutateAsync({ ui: formData })
 }

 const isRefreshIntervalValid = formData.refresh_interval >= SETTINGS_VALIDATION.ui.refresh_interval.min &&
  formData.refresh_interval <= SETTINGS_VALIDATION.ui.refresh_interval.max

 const isItemsPerPageValid = formData.items_per_page >= SETTINGS_VALIDATION.ui.items_per_page.min &&
  formData.items_per_page <= SETTINGS_VALIDATION.ui.items_per_page.max

 if (isLoading) return <div>Загрузка настроек...</div>

 return (
  <div className="space-y-6">
   <div>
    <h2 className="text-lg font-semibold">Настройки интерфейса</h2>
    <p className="text-sm text-slate-600 dark:text-slate-400">
     Персонализация пользовательского интерфейса
    </p>
   </div>

   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Monitor className="h-5 w-5" />
      Внешний вид
     </CardTitle>
     <CardDescription>
      Настройте тему и отображение интерфейса
     </CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
     <div className="space-y-2">
      <Label htmlFor="theme">Тема интерфейса</Label>
      <Select value={formData.theme} onValueChange={(value) => handleInputChange('theme', value)}>
       <SelectTrigger>
        <SelectValue placeholder="Выберите тему" />
       </SelectTrigger>
       <SelectContent>
        {THEME_OPTIONS.map((option) => (
         <SelectItem key={option.value} value={option.value}>
          {option.label}
         </SelectItem>
        ))}
       </SelectContent>
      </Select>
      <p className="text-xs text-slate-500">
       Цветовая схема интерфейса
      </p>
     </div>

     <div className="flex items-center justify-between">
      <div className="space-y-0.5">
       <Label htmlFor="auto_refresh">Автообновление данных</Label>
       <p className="text-xs text-slate-500">
        Автоматически обновлять данные на страницах
       </p>
      </div>
      <Switch
       id="auto_refresh"
       checked={formData.auto_refresh}
       onCheckedChange={(checked) => handleInputChange('auto_refresh', checked)}
      />
     </div>

     {formData.auto_refresh && (
      <div className="space-y-2">
       <Label htmlFor="refresh_interval" className="flex items-center gap-2">
        Интервал обновления (секунды)
        <Badge variant={isRefreshIntervalValid ? 'default' : 'destructive'}>
         {isRefreshIntervalValid ? 'Валидно' : 'Недопустимо'}
        </Badge>
       </Label>
       <Input
        id="refresh_interval"
        type="number"
        min={SETTINGS_VALIDATION.ui.refresh_interval.min}
        max={SETTINGS_VALIDATION.ui.refresh_interval.max}
        value={formData.refresh_interval}
        onChange={(e) => handleInputChange('refresh_interval', parseInt(e.target.value) || 30)}
       />
       <p className="text-xs text-slate-500">
        Как часто обновлять данные (от {SETTINGS_VALIDATION.ui.refresh_interval.min} до {SETTINGS_VALIDATION.ui.refresh_interval.max} сек)
       </p>
      </div>
     )}

     <div className="space-y-2">
      <Label htmlFor="items_per_page" className="flex items-center gap-2">
       Элементов на странице
       <Badge variant={isItemsPerPageValid ? 'default' : 'destructive'}>
        {isItemsPerPageValid ? 'Валидно' : 'Недопустимо'}
       </Badge>
      </Label>
      <Input
       id="items_per_page"
       type="number"
       min={SETTINGS_VALIDATION.ui.items_per_page.min}
       max={SETTINGS_VALIDATION.ui.items_per_page.max}
       value={formData.items_per_page}
       onChange={(e) => handleInputChange('items_per_page', parseInt(e.target.value) || 20)}
      />
      <p className="text-xs text-slate-500">
       Количество элементов в таблицах и списках
      </p>
     </div>

     <div className="flex items-center justify-between">
      <div className="space-y-0.5">
       <Label htmlFor="show_notifications">Показывать уведомления</Label>
       <p className="text-xs text-slate-500">
        Отображать toast-уведомления о действиях
       </p>
      </div>
      <Switch
       id="show_notifications"
       checked={formData.show_notifications}
       onCheckedChange={(checked) => handleInputChange('show_notifications', checked)}
      />
     </div>

     <div className="flex gap-3 pt-4">
      <Button
       onClick={handleSave}
       disabled={updateSettings.isPending || !isRefreshIntervalValid || !isItemsPerPageValid}
      >
       {updateSettings.isPending ? 'Сохранение...' : 'Сохранить'}
      </Button>
     </div>
    </CardContent>
   </Card>
  </div>
 )
} 