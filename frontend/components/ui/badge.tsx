import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-blue-500 text-slate-50 hover:bg-blue-500/80',
        secondary:
          'border-transparent bg-slate-700 text-slate-50 hover:bg-slate-700/80',
        destructive:
          'border-transparent bg-red-500 text-slate-50 hover:bg-red-500/80',
        success:
          'border-transparent bg-green-500 text-slate-50 hover:bg-green-500/80',
        warning:
          'border-transparent bg-yellow-500 text-slate-900 hover:bg-yellow-500/80',
        outline: 'text-slate-50 border-slate-700',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
