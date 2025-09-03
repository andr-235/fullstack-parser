'use client'

import { useState } from 'react'

import { Save, RefreshCw } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'

import { SettingsApi } from './SettingsApi'
import { SettingsAppearance } from './SettingsAppearance'
import { SettingsDatabase } from './SettingsDatabase'
import { SettingsFilters } from './SettingsFilters'
import { SettingsGeneral } from './SettingsGeneral'
import { SettingsList } from './SettingsList'
import { SettingsNotifications } from './SettingsNotifications'

export function SettingsPage() {
 const [isSaving, setIsSaving] = useState(false)
 const [isRefreshing, setIsRefreshing] = useState(false)
 const [error, setError] = useState<string | null>(null)
 const [filters, setFilters] = useState<{ categories?: string[], statuses?: string[] }>({})

 const handleSave = async () => {
  setIsSaving(true)
  setError(null)
  try {
   // Simulate API call
   await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (err) {
   setError('Не удалось сохранить настройки')
   console.error('Failed to save settings:', err)
  } finally {
   setIsSaving(false)
  }
 }

 const handleRefresh = async () => {
  setIsRefreshing(true)
  setError(null)
  try {
   // Simulate API call
   await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (err) {
   setError('Не удалось обновить настройки')
   console.error('Failed to refresh settings:', err)
  } finally {
   setIsRefreshing(false)
  }
 }

 return (
  <div className="container mx-auto py-6 space-y-6">
   {/* Header */}
   <div className="flex items-center justify-between">
    <div>
     <h1 className="text-3xl font-bold tracking-tight">Настройки</h1>
     <p className="text-muted-foreground">
      Управление настройками и конфигурацией приложения
     </p>
    </div>

    <div className="flex items-center gap-2">
     <Button
      variant="outline"
      onClick={handleRefresh}
      disabled={isRefreshing}
      className="gap-2"
     >
      <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
      Обновить
     </Button>
     <Button
      onClick={handleSave}
      disabled={isSaving}
      className="gap-2"
     >
      <Save className="h-4 w-4" />
      {isSaving ? 'Сохранение...' : 'Сохранить изменения'}
     </Button>
    </div>
   </div>

   {/* Error State */}
   {error && (
    <Alert className="border-destructive">
     <RefreshCw className="h-4 w-4" />
     <AlertDescription>
      {error}
      <Button
       variant="outline"
       size="sm"
       onClick={() => setError(null)}
       className="ml-4"
      >
       Закрыть
      </Button>
     </AlertDescription>
    </Alert>
   )}

   {/* Filters */}
   <SettingsFilters
    filters={filters}
    onFiltersChange={setFilters}
   />

   {/* Settings Overview */}
   <SettingsList loading={isRefreshing} />

   {/* Settings Tabs */}
   <Tabs defaultValue="general" className="space-y-4">
    <TabsList className="grid w-full grid-cols-5">
     <TabsTrigger value="general">Общие</TabsTrigger>
     <TabsTrigger value="api">API</TabsTrigger>
     <TabsTrigger value="database">База данных</TabsTrigger>
     <TabsTrigger value="notifications">Уведомления</TabsTrigger>
     <TabsTrigger value="appearance">Внешний вид</TabsTrigger>
    </TabsList>

    <TabsContent value="general" className="space-y-4">
     <SettingsGeneral />
    </TabsContent>

    <TabsContent value="api" className="space-y-4">
     <SettingsApi />
    </TabsContent>

    <TabsContent value="database" className="space-y-4">
     <SettingsDatabase />
    </TabsContent>

    <TabsContent value="notifications" className="space-y-4">
     <SettingsNotifications />
    </TabsContent>

    <TabsContent value="appearance" className="space-y-4">
     <SettingsAppearance />
    </TabsContent>
   </Tabs>
  </div>
 )
}
