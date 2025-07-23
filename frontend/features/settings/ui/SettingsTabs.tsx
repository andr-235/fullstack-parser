/**
 * Компонент с табами для настроек
 */

'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui'
import { VKAPISettingsTab } from './VKAPISettingsTab'
import { MonitoringSettingsTab } from './MonitoringSettingsTab'
import { DatabaseSettingsTab } from './DatabaseSettingsTab'
import { LoggingSettingsTab } from './LoggingSettingsTab'
import { UISettingsTab } from './UISettingsTab'

export function SettingsTabs() {
  const [activeTab, setActiveTab] = useState('vk-api')

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
      <TabsList className="grid w-full grid-cols-5">
        <TabsTrigger value="vk-api">VK API</TabsTrigger>
        <TabsTrigger value="monitoring">Мониторинг</TabsTrigger>
        <TabsTrigger value="database">База данных</TabsTrigger>
        <TabsTrigger value="logging">Логирование</TabsTrigger>
        <TabsTrigger value="ui">Интерфейс</TabsTrigger>
      </TabsList>

      <TabsContent value="vk-api" className="space-y-6">
        <VKAPISettingsTab />
      </TabsContent>

      <TabsContent value="monitoring" className="space-y-6">
        <MonitoringSettingsTab />
      </TabsContent>

      <TabsContent value="database" className="space-y-6">
        <DatabaseSettingsTab />
      </TabsContent>

      <TabsContent value="logging" className="space-y-6">
        <LoggingSettingsTab />
      </TabsContent>

      <TabsContent value="ui" className="space-y-6">
        <UISettingsTab />
      </TabsContent>
    </Tabs>
  )
}
