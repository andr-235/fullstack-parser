'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'

export function MonitoringResources() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Системные ресурсы</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-sm">Использование CPU</span>
          <span className="text-sm font-medium">45%</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div className="bg-primary h-2 rounded-full" style={{ width: '45%' }}></div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm">Использование памяти</span>
          <span className="text-sm font-medium">67%</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div className="bg-orange-500 h-2 rounded-full" style={{ width: '67%' }}></div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm">Использование диска</span>
          <span className="text-sm font-medium">23%</span>
        </div>
        <div className="w-full bg-secondary rounded-full h-2">
          <div className="bg-green-500 h-2 rounded-full" style={{ width: '23%' }}></div>
        </div>
      </CardContent>
    </Card>
  )
}
