'use client'

import * as React from 'react'
import { cn } from '@/shared/lib/utils'

export interface TimeStatsItem {
 label: string
 value: number | string
 description: string
 highlight?: boolean
}

export interface TimeStatsProps {
 title: string
 items: TimeStatsItem[]
 className?: string
 columns?: 1 | 2 | 3 | 4
}

export function TimeStats({
 title,
 items,
 className,
 columns = 2
}: TimeStatsProps) {
 const gridCols = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
 }

 return (
  <div className={cn('space-y-4', className)}>
   <h3 className="text-lg font-semibold text-foreground">{title}</h3>
   <div className={cn('grid gap-4', gridCols[columns])}>
    {items.map((item, index) => (
     <div
      key={index}
      className="flex justify-between items-center p-3 rounded-lg bg-card border"
     >
      <div>
       <span className="text-sm text-muted-foreground">{item.label}</span>
       <div className="text-xs text-muted-foreground">{item.description}</div>
      </div>
      <div className="text-right">
       <div className={cn(
        'font-semibold',
        item.highlight && 'text-primary'
       )}>
        {item.value}
       </div>
      </div>
     </div>
    ))}
   </div>
  </div>
 )
}
