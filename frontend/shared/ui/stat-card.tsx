'use client'

import { LucideIcon } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { Badge } from './badge'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  description?: string
  icon?: LucideIcon
  iconColor?: string
  trend?: boolean | undefined
  trendValue?: number
  className?: string
}

export function StatCard({
  title,
  value,
  description,
  icon: Icon,
  iconColor = 'text-muted-foreground',
  trend,
  trendValue,
  className,
}: StatCardProps) {
  const getTrendIcon = (isPositive: boolean | undefined) => {
    if (isPositive === undefined) return null
    return isPositive ? TrendingUp : TrendingDown
  }

  const getTrendVariant = (isPositive: boolean | undefined) => {
    if (isPositive === undefined) return 'secondary'
    return isPositive ? 'default' : 'destructive'
  }

  const TrendIcon = getTrendIcon(trend)

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className="flex items-center gap-2">
          {TrendIcon && trendValue !== undefined && (
            <Badge variant={getTrendVariant(trend)} className="text-xs px-1.5 py-0.5">
              <TrendIcon className="h-3 w-3 mr-1" />
              {Math.abs(trendValue).toFixed(0)}
            </Badge>
          )}
          {Icon && <Icon className={`h-4 w-4 ${iconColor}`} />}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && <p className="text-xs text-muted-foreground">{description}</p>}
      </CardContent>
    </Card>
  )
}