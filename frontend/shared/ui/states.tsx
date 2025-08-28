'use client'

import * as React from 'react'
import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { LoadingSpinner } from '@/shared/ui'
import { RefreshCw, FileX, Search, AlertCircle, type LucideIcon } from 'lucide-react'
import { cn } from '@/shared/lib/utils'

/**
 * Компонент состояния загрузки
 */
interface LoadingStateProps {
 message?: string
 className?: string
 size?: 'sm' | 'md' | 'lg'
 fullHeight?: boolean
}

export function LoadingState({
 message = 'Загрузка...',
 className,
 size = 'lg',
 fullHeight = true,
}: LoadingStateProps) {
 return (
  <div
   className={cn(
    'flex items-center justify-center',
    fullHeight && 'min-h-[200px]',
    className
   )}
  >
   <div className="flex flex-col items-center justify-center space-y-4">
    <LoadingSpinner size={size} />
    <span className="text-muted-foreground font-medium">{message}</span>
   </div>
  </div>
 )
}

/**
 * Компонент пустого состояния
 */
interface EmptyStateProps {
 icon?: LucideIcon
 title: string
 description?: string
 action?: {
  label: string
  onClick: () => void
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive'
 } | undefined
 className?: string | undefined
 fullHeight?: boolean
}

export function EmptyState({
 icon: Icon = FileX,
 title,
 description,
 action,
 className,
 fullHeight = true,
}: EmptyStateProps) {
 return (
  <div
   className={cn(
    'flex items-center justify-center',
    fullHeight && 'min-h-[200px]',
    className
   )}
  >
   <div className="text-center space-y-4">
    <div className="mx-auto w-12 h-12 bg-muted rounded-full flex items-center justify-center">
     <Icon className="w-6 h-6 text-muted-foreground" />
    </div>
    <div className="space-y-2">
     <h3 className="text-lg font-semibold">{title}</h3>
     {description && (
      <p className="text-muted-foreground max-w-sm">{description}</p>
     )}
    </div>
    {action && (
     <Button onClick={action.onClick} variant={action.variant || 'outline'}>
      {action.label}
     </Button>
    )}
   </div>
  </div>
 )
}

/**
 * Компонент состояния ошибки
 */
interface ErrorStateProps {
 title?: string
 message?: string
 onRetry?: () => void
 retryLabel?: string
 className?: string
 fullHeight?: boolean
 showIcon?: boolean
}

export function ErrorState({
 title = 'Произошла ошибка',
 message = 'Не удалось загрузить данные. Попробуйте обновить страницу.',
 onRetry,
 retryLabel = 'Обновить',
 className,
 fullHeight = true,
 showIcon = true,
}: ErrorStateProps) {
 return (
  <div
   className={cn(
    'flex items-center justify-center',
    fullHeight && 'min-h-[200px]',
    className
   )}
  >
   <Card className="w-full max-w-md border-destructive/20">
    <CardHeader className="text-center">
     {showIcon && (
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
       <AlertCircle className="h-6 w-6 text-destructive" />
      </div>
     )}
     <CardTitle className="text-destructive">{title}</CardTitle>
    </CardHeader>
    <CardContent className="text-center space-y-4">
     <p className="text-muted-foreground">{message}</p>
     {onRetry && (
      <Button onClick={onRetry} variant="outline" className="w-full">
       <RefreshCw className="h-4 w-4 mr-2" />
       {retryLabel}
      </Button>
     )}
    </CardContent>
   </Card>
  </div>
 )
}

/**
 * Компонент состояния поиска (ничего не найдено)
 */
interface NoResultsStateProps {
 searchQuery?: string
 onClearSearch?: () => void
 className?: string
 fullHeight?: boolean
}

export function NoResultsState({
 searchQuery,
 onClearSearch,
 className,
 fullHeight = true,
}: NoResultsStateProps) {
 return (
  <EmptyState
   icon={Search}
   title="Ничего не найдено"
   description={
    searchQuery
     ? `По запросу "${searchQuery}" ничего не найдено.`
     : 'Попробуйте изменить критерии поиска.'
   }
   action={
    onClearSearch
     ? {
      label: 'Очистить поиск',
      onClick: onClearSearch,
      variant: 'outline',
     }
     : undefined
   }
   className={className}
   fullHeight={fullHeight}
  />
 )
}
