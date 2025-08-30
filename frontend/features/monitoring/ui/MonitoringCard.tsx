'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { LucideIcon } from 'lucide-react'

interface MonitoringCardProps {
 title: string
 icon: LucideIcon
 value?: string | number
 description?: string
 status?: 'success' | 'warning' | 'error' | 'info'
 indicator?: 'pulse' | 'static'
}

export function MonitoringCard({
 title,
 icon: Icon,
 value,
 description,
 status = 'info',
 indicator = 'static'
}: MonitoringCardProps) {
 const getStatusColor = () => {
  switch (status) {
   case 'success':
    return 'text-green-500'
   case 'warning':
    return 'text-orange-500'
   case 'error':
    return 'text-red-500'
   default:
    return 'text-muted-foreground'
  }
 }

 const getIndicatorColor = () => {
  switch (status) {
   case 'success':
    return 'bg-green-500'
   case 'warning':
    return 'bg-orange-500'
   case 'error':
    return 'bg-red-500'
   default:
    return 'bg-gray-400'
  }
 }

 return (
  <Card>
   <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
    <CardTitle className="text-sm font-medium">{title}</CardTitle>
    <Icon className={`h-4 w-4 ${getStatusColor()}`} />
   </CardHeader>
   <CardContent>
    {value !== undefined ? (
     <div className="space-y-1">
      <div className="text-2xl font-bold">{value}</div>
      {description && (
       <p className="text-xs text-muted-foreground">{description}</p>
      )}
     </div>
    ) : (
     <div className="flex items-center gap-2">
      {indicator === 'pulse' && (
       <div className={`h-2 w-2 ${getIndicatorColor()} rounded-full animate-pulse`}></div>
      )}
      {indicator === 'static' && (
       <div className={`h-2 w-2 ${getIndicatorColor()} rounded-full`}></div>
      )}
      <span className="text-sm font-medium">{description}</span>
     </div>
    )}
   </CardContent>
  </Card>
 )
}
