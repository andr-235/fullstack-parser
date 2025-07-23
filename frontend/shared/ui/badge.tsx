import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/shared/lib/utils'

const badgeVariants = cva(
  // Строгая рамка, минимум скруглений, строгие цвета
  'inline-flex items-center border rounded-sm px-2 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-700 focus:ring-offset-2 focus:ring-offset-slate-900',
  {
    variants: {
      variant: {
        default: 'bg-slate-800 text-slate-100 border-slate-700',
        success: 'bg-green-700 text-white border-green-800',
        destructive: 'bg-red-700 text-white border-red-800',
        secondary: 'bg-slate-700 text-slate-300 border-slate-600',
        outline: 'bg-transparent text-slate-100 border-slate-500',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(badgeVariants({ variant }), className)}
        {...props}
      />
    )
  }
)
Badge.displayName = 'Badge'

export { Badge, badgeVariants }
