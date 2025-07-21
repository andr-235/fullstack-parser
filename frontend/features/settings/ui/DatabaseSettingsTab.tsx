/**
 * Таб настроек базы данных
 */

'use client'

import { useState } from 'react'
import { useSettings, useUpdateSettings } from '@/hooks/use-settings'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Database } from 'lucide-react'
import { SETTINGS_VALIDATION } from '@/types/settings'

export function DatabaseSettingsTab() {
 const { data: settingsData, isLoading } = useSettings()
 const updateSettings = useUpdateSettings()

 const [formData, setFormData] = useState({
  pool_size: 10,
  max_overflow: 20,
  pool_recycle: 3600,
 })

 if (settingsData && !isLoading && formData.pool_size === 10) {
  setFormData({
   pool_size: settingsData.settings.database.pool_size,
   max_overflow: settingsData.settings.database.max_overflow,
   pool_recycle: settingsData.settings.database.pool_recycle,
  })
 }

 const handleInputChange = (field: string, value: number) => {
  setFormData(prev => ({ ...prev, [field]: value }))
 }

 const handleSave = async () => {
  await updateSettings.mutateAsync({ database: formData })
 }

 const isPoolSizeValid = formData.pool_size >= SETTINGS_VALIDATION.database.pool_size.min &&
  formData.pool_size <= SETTINGS_VALIDATION.database.pool_size.max

 const isMaxOverflowValid = formData.max_overflow >= SETTINGS_VALIDATION.database.max_overflow.min &&
  formData.max_overflow <= SETTINGS_VALIDATION.database.max_overflow.max

 const isPoolRecycleValid = formData.pool_recycle >= SETTINGS_VALIDATION.database.pool_recycle.min &&
  formData.pool_recycle <= SETTINGS_VALIDATION.database.pool_recycle.max

 if (isLoading) return <div>Загрузка настроек...</div>

 return (
  <div className="space-y-6">
   <div>
    <h2 className="text-lg font-semibold">Настройки базы данных</h2>
    <p className="text-sm text-slate-600 dark:text-slate-400">
     Конфигурация пула соединений с базой данных
    </p>
   </div>

   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Database className="h-5 w-5" />
      Пул соединений
     </CardTitle>
     <CardDescription>
      Настройте параметры пула соединений PostgreSQL
     </CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
     <div className="space-y-2">
      <Label htmlFor="pool_size" className="flex items-center gap-2">
       Размер пула
       <Badge variant={isPoolSizeValid ? 'default' : 'destructive'}>
        {isPoolSizeValid ? 'Валидно' : 'Недопустимо'}
       </Badge>
      </Label>
      <Input
       id="pool_size"
       type="number"
       min={SETTINGS_VALIDATION.database.pool_size.min}
       max={SETTINGS_VALIDATION.database.pool_size.max}
       value={formData.pool_size}
       onChange={(e) => handleInputChange('pool_size', parseInt(e.target.value) || 10)}
      />
      <p className="text-xs text-slate-500">
       Количество постоянных соединений в пуле
      </p>
     </div>

     <div className="space-y-2">
      <Label htmlFor="max_overflow" className="flex items-center gap-2">
       Макс. переполнение
       <Badge variant={isMaxOverflowValid ? 'default' : 'destructive'}>
        {isMaxOverflowValid ? 'Валидно' : 'Недопустимо'}
       </Badge>
      </Label>
      <Input
       id="max_overflow"
       type="number"
       min={SETTINGS_VALIDATION.database.max_overflow.min}
       max={SETTINGS_VALIDATION.database.max_overflow.max}
       value={formData.max_overflow}
       onChange={(e) => handleInputChange('max_overflow', parseInt(e.target.value) || 20)}
      />
      <p className="text-xs text-slate-500">
       Максимальное количество дополнительных соединений
      </p>
     </div>

     <div className="space-y-2">
      <Label htmlFor="pool_recycle" className="flex items-center gap-2">
       Пересоздание (секунды)
       <Badge variant={isPoolRecycleValid ? 'default' : 'destructive'}>
        {isPoolRecycleValid ? 'Валидно' : 'Недопустимо'}
       </Badge>
      </Label>
      <Input
       id="pool_recycle"
       type="number"
       min={SETTINGS_VALIDATION.database.pool_recycle.min}
       max={SETTINGS_VALIDATION.database.pool_recycle.max}
       value={formData.pool_recycle}
       onChange={(e) => handleInputChange('pool_recycle', parseInt(e.target.value) || 3600)}
      />
      <p className="text-xs text-slate-500">
       Интервал пересоздания соединений
      </p>
     </div>

     <div className="flex gap-3 pt-4">
      <Button
       onClick={handleSave}
       disabled={updateSettings.isPending || !isPoolSizeValid || !isMaxOverflowValid || !isPoolRecycleValid}
      >
       {updateSettings.isPending ? 'Сохранение...' : 'Сохранить'}
      </Button>
     </div>
    </CardContent>
   </Card>
  </div>
 )
} 