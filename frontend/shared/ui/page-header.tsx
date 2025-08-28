'use client'

import * as React from 'react'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { LucideIcon } from 'lucide-react'

export interface PageHeaderProps {
 title: string
 description?: string
 icon?: LucideIcon
 badge?: {
  text: string
  variant?: 'default' | 'secondary' | 'destructive' | 'outline'
 }
 actions?: React.ReactNode
 className?: string
 gradient?: boolean
}

/**
 * Универсальный компонент заголовка страницы
 * Заменяет повторяющиеся паттерны заголовков с иконками, описаниями и действиями
 */
export function PageHeader({
 title,
 description,
 icon: Icon,
 badge,
 actions,
 className,
 gradient = false,
}: PageHeaderProps) {
 return (
  <div
   className={cn(
    'w-full',
    gradient && 'bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white',
    !gradient && 'space-y-2',
    className
   )}
  >
   <div className="flex items-center space-x-3 mb-2">
    {Icon && (
     <div className={cn(
      'p-2 rounded-lg',
      gradient ? 'bg-white/10' : 'bg-muted'
     )}>
      <Icon className={cn(
       'h-6 w-6',
       gradient ? 'text-white' : 'text-muted-foreground'
      )} />
     </div>
    )}
    <h1 className={cn(
     'text-2xl font-bold',
     gradient ? 'text-white' : 'text-foreground'
    )}>
     {title}
    </h1>
    {badge && (
     <Badge
      variant={badge.variant || 'secondary'}
      className={gradient ? 'bg-white/10 text-white border-white/20' : ''}
     >
      {badge.text}
     </Badge>
    )}
   </div>

   {description && (
    <p className={cn(
     gradient ? 'text-slate-300' : 'text-muted-foreground'
    )}>
     {description}
    </p>
   )}

   {actions && (
    <div className={cn(
     'flex items-center gap-2 mt-4',
     gradient ? 'justify-end' : 'justify-start'
    )}>
     {actions}
    </div>
   )}
  </div>
 )
}

/**
 * Компактная версия заголовка для использования в карточках или боковых панелях
 */
export function CompactPageHeader({
 title,
 description,
 icon: Icon,
 className,
}: Omit<PageHeaderProps, 'badge' | 'actions' | 'gradient'>) {
 return (
  <div className={cn('flex items-start space-x-3', className)}>
   {Icon && (
    <div className="p-1 bg-muted rounded">
     <Icon className="h-4 w-4 text-muted-foreground" />
    </div>
   )}
   <div className="flex-1 min-w-0">
    <h3 className="font-semibold text-foreground truncate">{title}</h3>
    {description && (
     <p className="text-sm text-muted-foreground mt-1">{description}</p>
    )}
   </div>
  </div>
 )
}
