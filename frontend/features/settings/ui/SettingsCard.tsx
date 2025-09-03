'use client'

import { LucideIcon } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

interface SettingsCardProps {
 title: string
 icon: LucideIcon
 value?: string | number
 description?: string
 status?: 'active' | 'inactive' | 'warning' | 'info'
 badge?: string
}

export function SettingsCard({
 title,
 icon: Icon,
 value,
 description,
 status = 'info',
 badge
}: SettingsCardProps) {
 const getStatusColor = () => {
  switch (status) {
   case 'active':
    return 'text-green-500'
   case 'inactive':
    return 'text-gray-500'
   case 'warning':
    return 'text-orange-500'
   default:
    return 'text-blue-500'
  }
 }

 return (
  <Card className="group hover:shadow-md transition-shadow">
   <CardHeader className="pb-3">
    <div className="flex items-start justify-between">
     <div className="flex items-center gap-3">
      <Icon className={`h-5 w-5 ${getStatusColor()}`} />
      <div className="min-w-0 flex-1">
       <CardTitle className="text-sm font-medium truncate">{title}</CardTitle>
       {description && (
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
       )}
      </div>
     </div>
     {badge && (
      <Badge variant="secondary" className="text-xs">
       {badge}
      </Badge>
     )}
    </div>
   </CardHeader>

   {value !== undefined && (
    <CardContent className="pt-0">
     <div className="text-lg font-semibold">{value}</div>
    </CardContent>
   )}
  </Card>
 )
}
