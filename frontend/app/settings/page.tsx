/**
 * Страница настроек приложения
 */

'use client'

import { Suspense } from 'react'
import { SettingsTabs } from '@/features/settings/ui/SettingsTabs'
import { SettingsHeader } from '@/features/settings/ui/SettingsHeader'
import { SettingsHealthWidget } from '@/features/settings/ui/SettingsHealthWidget'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <SettingsHeader />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Основные настройки */}
        <div className="lg:col-span-3">
          <Card className="border-slate-700 bg-slate-800 shadow-lg">
            <CardContent className="p-6">
              <Suspense fallback={<SettingsSkeleton />}>
                <SettingsTabs />
              </Suspense>
            </CardContent>
          </Card>
        </div>

        {/* Виджет здоровья системы */}
        <div className="lg:col-span-1">
          <Suspense fallback={<HealthSkeleton />}>
            <SettingsHealthWidget />
          </Suspense>
        </div>
      </div>
    </div>
  )
}

function SettingsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48 bg-slate-700" />
        <Skeleton className="h-4 w-96 bg-slate-700" />
      </div>
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-6 w-32 bg-slate-700" />
            <Skeleton className="h-10 w-full bg-slate-700" />
          </div>
        ))}
      </div>
    </div>
  )
}

function HealthSkeleton() {
  return (
    <Card className="border-slate-700 bg-slate-800 shadow-lg">
      <CardContent className="p-6">
        <div className="space-y-4">
          <Skeleton className="h-6 w-32 bg-slate-700" />
          <div className="space-y-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton className="h-4 w-24 bg-slate-700" />
                <Skeleton className="h-4 w-16 bg-slate-700" />
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
