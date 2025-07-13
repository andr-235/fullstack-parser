import * as React from 'react'
import { cn } from '@/shared/lib/utils'

interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg'
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  className,
  size = 'md',
  ...props
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  }

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
        sizeClasses[size],
        className
      )}
      {...props}
    />
  )
}

const LoadingSpinnerWithText: React.FC<{
  text?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}> = ({ text = 'Загрузка...', size = 'md', className }) => {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <LoadingSpinner size={size} />
      <span className="text-sm text-gray-600">{text}</span>
    </div>
  )
}

export { LoadingSpinner, LoadingSpinnerWithText }
