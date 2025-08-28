'use client'

import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { cn } from '@/shared/lib/utils'
import { RefreshCw, AlertTriangle, ChevronDown, ChevronUp, ExternalLink, type LucideIcon } from 'lucide-react'

export interface ErrorCardProps {
 /** Заголовок ошибки */
 title?: string
 /** Сообщение об ошибке */
 message?: string
 /** Детали ошибки (для разработчиков) */
 details?: string | Error
 /** Код ошибки */
 code?: string | number
 /** Действия для исправления ошибки */
 actions?: Array<{
  label: string
  onClick: () => void
  variant?: 'default' | 'outline' | 'secondary' | 'ghost' | 'link' | 'destructive'
  icon?: LucideIcon
 }>
 /** Показывать ли детали по умолчанию */
 showDetails?: boolean
 /** Кастомная иконка */
 icon?: LucideIcon
 /** Размер карточки */
 size?: 'sm' | 'md' | 'lg'
 /** Классы для стилизации */
 className?: string
 /** Полноэкранный режим */
 fullScreen?: boolean
}

/**
 * Универсальный компонент для отображения ошибок
 * Заменяет повторяющиеся паттерны обработки ошибок
 */
export function ErrorCard({
 title = 'Произошла ошибка',
 message = 'Не удалось выполнить операцию. Попробуйте еще раз.',
 details,
 code,
 actions = [],
 showDetails = false,
 icon: Icon = AlertTriangle,
 size = 'md',
 className,
 fullScreen = false,
}: ErrorCardProps) {
 const [isDetailsOpen, setIsDetailsOpen] = React.useState(showDetails)

 const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
 }

 const cardClasses = cn(
  'border-destructive/20',
  fullScreen && 'min-h-screen flex items-center justify-center',
  sizeClasses[size],
  className
 )

 const containerClasses = cn(
  'w-full',
  fullScreen ? 'min-h-screen flex items-center justify-center p-4' : ''
 )

 const content = (
  <Card className={cardClasses}>
   <CardHeader className="text-center">
    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
     <Icon className="h-6 w-6 text-destructive" />
    </div>

    <CardTitle className="text-destructive text-lg">
     {title}
    </CardTitle>

    {code && (
     <Badge variant="outline" className="mt-2 text-xs">
      Код: {code}
     </Badge>
    )}
   </CardHeader>

   <CardContent className="text-center space-y-4">
    <p className="text-muted-foreground">{message}</p>

    {details && (
     <div className="space-y-2">
      <button
       onClick={() => setIsDetailsOpen(!isDetailsOpen)}
       className="flex items-center justify-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
       {isDetailsOpen ? (
        <>
         <ChevronUp className="h-4 w-4" />
         Скрыть детали
        </>
       ) : (
        <>
         <ChevronDown className="h-4 w-4" />
         Показать детали
        </>
       )}
      </button>

      {isDetailsOpen && (
       <div className="text-left p-3 bg-muted/50 rounded-md text-xs font-mono text-foreground overflow-auto max-h-32">
        {typeof details === 'string' ? details : details.message}
        {details instanceof Error && details.stack && (
         <pre className="mt-2 whitespace-pre-wrap">
          {details.stack}
         </pre>
        )}
       </div>
      )}
     </div>
    )}

    {actions.length > 0 && (
     <div className="flex flex-col sm:flex-row gap-2 justify-center pt-2">
      {actions.map((action, index) => {
       const ActionIcon = action.icon
       return (
        <Button
         key={index}
         onClick={action.onClick}
         variant={action.variant || 'outline'}
         className="flex items-center gap-2"
        >
         {ActionIcon && <ActionIcon className="h-4 w-4" />}
         {action.label}
        </Button>
       )
      })}
     </div>
    )}
   </CardContent>
  </Card>
 )

 if (fullScreen) {
  return <div className={containerClasses}>{content}</div>
 }

 return content
}

/**
 * Компонент для сетки ошибок
 */
export function ErrorsGrid({
 errors,
 className,
}: {
 errors: Array<Omit<ErrorCardProps, 'fullScreen'>>
 className?: string
}) {
 return (
  <div className={cn('grid gap-4 md:grid-cols-2 lg:grid-cols-3', className)}>
   {errors.map((error, index) => (
    <ErrorCard key={index} {...error} />
   ))}
  </div>
 )
}

/**
 * Простая версия для быстрого использования
 */
export function SimpleErrorCard({
 title = 'Ошибка',
 message = 'Что-то пошло не так',
 onRetry,
 retryLabel = 'Попробовать снова',
}: {
 title?: string
 message?: string
 onRetry?: () => void
 retryLabel?: string
}) {
 return (
  <ErrorCard
   title={title}
   message={message}
   actions={
    onRetry
     ? [
      {
       label: retryLabel,
       onClick: onRetry,
       icon: RefreshCw,
      },
     ]
     : []
   }
  />
 )
}

/**
 * Компонент для отображения сетевых ошибок
 */
export function NetworkErrorCard({
 onRetry,
 onGoHome,
}: {
 onRetry?: () => void
 onGoHome?: () => void
}) {
 const actions = []

 if (onRetry) {
  actions.push({
   label: 'Попробовать снова',
   onClick: onRetry,
   icon: RefreshCw,
  })
 }

 if (onGoHome) {
  actions.push({
   label: 'На главную',
   onClick: onGoHome,
   icon: ExternalLink,
   variant: 'outline' as const,
  })
 }

 return (
  <ErrorCard
   title="Ошибка сети"
   message="Не удалось подключиться к серверу. Проверьте подключение к интернету и попробуйте еще раз."
   code="NETWORK_ERROR"
   actions={actions}
  />
 )
}
