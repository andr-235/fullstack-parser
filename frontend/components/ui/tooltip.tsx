'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'

interface TooltipContextType {
  isVisible: boolean
  setIsVisible: (visible: boolean) => void
}

const TooltipContext = React.createContext<TooltipContextType | undefined>(
  undefined
)

export function TooltipProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}

export function Tooltip({ children }: { children: React.ReactNode }) {
  const [isVisible, setIsVisible] = React.useState(false)

  return (
    <TooltipContext.Provider value={{ isVisible, setIsVisible }}>
      {children}
    </TooltipContext.Provider>
  )
}

export function TooltipTrigger({
  children,
  asChild = false,
}: {
  children: React.ReactNode
  asChild?: boolean
}) {
  const context = React.useContext(TooltipContext)

  if (!context) {
    return <>{children}</>
  }

  const { setIsVisible } = context

  const handleMouseEnter = () => setIsVisible(true)
  const handleMouseLeave = () => setIsVisible(false)

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<any>, {
      onMouseEnter: handleMouseEnter,
      onMouseLeave: handleMouseLeave,
    })
  }

  return (
    <div onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
      {children}
    </div>
  )
}

export function TooltipContent({
  children,
  className,
  side = 'top',
  align = 'center',
}: {
  children: React.ReactNode
  className?: string
  side?: 'top' | 'bottom' | 'left' | 'right'
  align?: 'start' | 'center' | 'end'
}) {
  const context = React.useContext(TooltipContext)

  if (!context || !context.isVisible) {
    return null
  }

  const { isVisible } = context

  const getPositionClasses = () => {
    const baseClasses =
      'absolute z-50 px-2 py-1 text-xs text-white bg-slate-800 rounded-md shadow-lg whitespace-nowrap'

    switch (side) {
      case 'top':
        return cn(
          baseClasses,
          'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
          'after:content-[""] after:absolute after:top-full after:left-1/2 after:transform after:-translate-x-1/2',
          'after:border-4 after:border-transparent after:border-t-slate-800'
        )
      case 'bottom':
        return cn(
          baseClasses,
          'top-full left-1/2 transform -translate-x-1/2 mt-2',
          'after:content-[""] after:absolute after:bottom-full after:left-1/2 after:transform after:-translate-x-1/2',
          'after:border-4 after:border-transparent after:border-b-slate-800'
        )
      case 'left':
        return cn(
          baseClasses,
          'right-full top-1/2 transform -translate-y-1/2 mr-2',
          'after:content-[""] after:absolute after:right-full after:top-1/2 after:transform after:-translate-y-1/2',
          'after:border-4 after:border-transparent after:border-l-slate-800'
        )
      case 'right':
        return cn(
          baseClasses,
          'left-full top-1/2 transform -translate-y-1/2 ml-2',
          'after:content-[""] after:absolute after:left-full after:top-1/2 after:transform after:-translate-y-1/2',
          'after:border-4 after:border-transparent after:border-r-slate-800'
        )
      default:
        return baseClasses
    }
  }

  return (
    <div className={cn('relative inline-block')}>
      <div className={cn(getPositionClasses(), className)}>{children}</div>
    </div>
  )
}
