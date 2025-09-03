'use client'

import { Activity } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'

interface MonitoringEvent {
 id: string
 type: 'success' | 'warning' | 'error' | 'info'
 message: string
 timestamp: string
}

interface MonitoringListProps {
 events: MonitoringEvent[]
 loading?: boolean
}

export function MonitoringList({ events, loading }: MonitoringListProps) {
 const getEventIcon = (type: string) => {
  switch (type) {
   case 'success':
    return '✅'
   case 'warning':
    return '⚠️'
   case 'error':
    return '❌'
   default:
    return 'ℹ️'
  }
 }

 const getEventColor = (type: string) => {
  switch (type) {
   case 'success':
    return 'text-green-500'
   case 'warning':
    return 'text-orange-500'
   case 'error':
    return 'text-red-500'
   default:
    return 'text-blue-500'
  }
 }

 if (loading) {
  return (
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Activity className="h-5 w-5" />
      Недавняя активность
     </CardTitle>
    </CardHeader>
    <CardContent>
     <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
       <div key={i} className="flex items-start gap-3 p-3 rounded-lg border">
        <div className="h-4 w-4 bg-gray-200 rounded animate-pulse mt-1"></div>
        <div className="flex-1 space-y-2">
         <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
         <div className="h-3 bg-gray-200 rounded animate-pulse w-24"></div>
        </div>
       </div>
      ))}
     </div>
    </CardContent>
   </Card>
  )
 }

 if (events.length === 0) {
  return (
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Activity className="h-5 w-5" />
      Недавняя активность
     </CardTitle>
    </CardHeader>
    <CardContent>
     <div className="flex flex-col items-center justify-center py-8 text-center">
      <Activity className="h-12 w-12 text-muted-foreground mb-4" />
      <p className="text-muted-foreground">Нет недавней активности</p>
      <p className="text-sm text-muted-foreground">
       События системы будут отображаться здесь
      </p>
     </div>
    </CardContent>
   </Card>
  )
 }

 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Activity className="h-5 w-5" />
     Недавняя активность
    </CardTitle>
   </CardHeader>
   <CardContent>
    <div className="space-y-4">
     {events.map((event) => (
      <div key={event.id} className="flex items-start gap-3 p-3 rounded-lg border">
       <span className={`text-lg mt-1 ${getEventColor(event.type)}`}>
        {getEventIcon(event.type)}
       </span>
       <div className="flex-1">
        <p className="text-sm font-medium">{event.message}</p>
        <p className="text-xs text-muted-foreground">{event.timestamp}</p>
       </div>
      </div>
     ))}
    </div>
   </CardContent>
  </Card>
 )
}
