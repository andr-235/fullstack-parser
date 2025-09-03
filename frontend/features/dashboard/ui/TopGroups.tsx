'use client'

import { Users, ExternalLink, TrendingUp, MessageSquare, BarChart3 } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Progress } from '@/shared/ui'

import { DashboardTopItem } from '@/entities/dashboard'

interface TopGroupsProps {
 groups: DashboardTopItem[]
}

export function TopGroups({ groups }: TopGroupsProps) {
 // Находим максимальное значение для расчета прогресса
 const maxCount = groups.length > 0 ? Math.max(...groups.map(g => g.count)) : 0

 if (groups.length === 0) {
  return (
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Users className="h-5 w-5" />
      Топ групп по активности
     </CardTitle>
    </CardHeader>
    <CardContent>
     <div className="flex flex-col items-center justify-center py-8 text-center">
      <Users className="h-12 w-12 text-muted-foreground mb-4" />
      <p className="text-muted-foreground">Данные о группах недоступны</p>
      <p className="text-sm text-muted-foreground">
       Группы появятся здесь после парсинга комментариев
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
     <BarChart3 className="h-5 w-5" />
     Топ групп по активности
    </CardTitle>
   </CardHeader>
   <CardContent>
    <div className="space-y-4">
     {groups.slice(0, 5).map((group, index) => {
      const progressValue = maxCount > 0 ? (group.count / maxCount) * 100 : 0
      const isTop = index < 3

      return (
       <div key={index} className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10">
         <span className="text-sm font-medium text-primary">
          {index + 1}
         </span>
        </div>

        <div className="flex-1 min-w-0">
         <div className="flex items-center justify-between mb-2">
          <p className="font-medium text-sm truncate">{group.name}</p>
          <div className="flex items-center gap-2">
           {isTop && (
            <Badge variant="default" className="text-xs">
             <TrendingUp className="h-3 w-3 mr-1" />
             Топ
            </Badge>
           )}
           <Badge variant="outline" className="text-xs">
            <MessageSquare className="h-3 w-3 mr-1" />
            {group.count}
           </Badge>
          </div>
         </div>

         <div className="flex items-center gap-2">
          <Progress value={progressValue} className="flex-1 h-2" />
          <span className="text-xs text-muted-foreground min-w-[3rem]">
           {progressValue.toFixed(0)}%
          </span>
         </div>
        </div>

        <Button variant="ghost" size="sm" className="flex-shrink-0">
         <ExternalLink className="h-4 w-4" />
        </Button>
       </div>
      )
     })}
    </div>

    {groups.length > 5 && (
     <div className="mt-4 pt-4 border-t">
      <p className="text-sm text-muted-foreground mb-3">
       И ещё {groups.length - 5} групп с активностью
      </p>
      <Button variant="outline" className="w-full">
       Показать все группы
      </Button>
     </div>
    )}
   </CardContent>
  </Card>
 )
}
