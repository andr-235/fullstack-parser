'use client'

import * as React from 'react'
import { cn } from '@/shared/lib/utils'

export interface PageContainerProps {
 /** Содержимое страницы */
 children: React.ReactNode
 /** Максимальная ширина контейнера */
 maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl' | 'full'
 /** Внутренние отступы */
 padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
 /** Центрирование контента */
 centered?: boolean
 /** Классы для стилизации */
 className?: string
 /** Фон страницы */
 background?: 'default' | 'muted' | 'gradient'
}

/**
 * Универсальный контейнер для страниц
 * Обеспечивает единообразное расположение и отступы
 */
export function PageContainer({
 children,
 maxWidth = '4xl',
 padding = 'lg',
 centered = false,
 className,
 background = 'default',
}: PageContainerProps) {
 const maxWidthClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
  '4xl': 'max-w-4xl',
  '6xl': 'max-w-6xl',
  full: 'max-w-full',
 }

 const paddingClasses = {
  none: 'p-0',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
  xl: 'p-12',
 }

 const backgroundClasses = {
  default: '',
  muted: 'bg-muted/30',
  gradient: 'bg-gradient-to-br from-background via-background to-muted/20',
 }

 return (
  <div className={cn(
   'w-full min-h-full',
   backgroundClasses[background],
   className
  )}>
   <div className={cn(
    'mx-auto',
    maxWidthClasses[maxWidth],
    paddingClasses[padding],
    centered && 'flex flex-col items-center justify-center min-h-full'
   )}>
    {children}
   </div>
  </div>
 )
}

/**
 * Компактная версия контейнера для форм и модальных окон
 */
interface CompactContainerProps extends Omit<PageContainerProps, 'maxWidth' | 'centered'> {
 /** Размер компактного контейнера */
 size?: 'sm' | 'md' | 'lg'
 /** Отступы для компактного контейнера */
 padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
}

export function CompactContainer({
 children,
 size = 'md',
 padding = 'sm',
 className,
 background = 'default',
}: CompactContainerProps) {
 const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
 }

 const paddingClasses = {
  none: 'p-0',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
  xl: 'p-12',
 }

 const backgroundClasses = {
  default: '',
  muted: 'bg-muted/30',
  gradient: 'bg-gradient-to-br from-background via-background to-muted/20',
 }

 return (
  <div className={cn(
   'w-full',
   backgroundClasses[background],
   className
  )}>
   <div className={cn(
    'mx-auto',
    sizeClasses[size],
    paddingClasses[padding]
   )}>
    {children}
   </div>
  </div>
 )
}
