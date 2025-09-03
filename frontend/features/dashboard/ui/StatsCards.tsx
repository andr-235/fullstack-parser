'use client'

import { MessageSquare, Users, Hash, FolderOpen, TrendingUp, TrendingDown, Target, Calendar } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

import { GlobalStats } from '@/entities/dashboard'
import { useDashboardMetrics, useTrends } from '@/entities/dashboard'


interface StatsCardsProps {
 stats: GlobalStats
}

export function StatsCards({ stats }: StatsCardsProps) {
 const { metrics } = useDashboardMetrics()
 const { trends } = useTrends()

 const getTrendIcon = (isPositive: boolean | undefined) => {
  if (isPositive === undefined) return null
  return isPositive ? TrendingUp : TrendingDown
 }

 const getTrendVariant = (isPositive: boolean | undefined) => {
  if (isPositive === undefined) return 'secondary'
  return isPositive ? 'default' : 'destructive'
 }

 const statCards = [
  {
   title: 'Комментарии сегодня',
   value: metrics?.today_comments.toLocaleString() || '0',
   description: `${metrics?.week_comments || 0} за неделю`,
   icon: MessageSquare,
   trend: trends?.comments_trend?.is_positive,
   trendValue: trends?.comments_trend?.today_vs_average,
  },
  {
   title: 'Совпадений сегодня',
   value: metrics?.today_matches.toLocaleString() || '0',
   description: `${metrics?.week_matches || 0} за неделю`,
   icon: Target,
   trend: trends?.matches_trend?.is_positive,
   trendValue: trends?.matches_trend?.today_vs_average,
  },
  {
   title: 'Активные группы',
   value: stats.active_groups.toString(),
   description: `из ${stats.total_groups} всего`,
   icon: Users,
   trend: stats.active_groups > stats.total_groups * 0.5,
  },
  {
   title: 'Процент совпадений',
   value: metrics?.match_rate ? `${metrics.match_rate.toFixed(1)}%` : '0%',
   description: 'комментарии с ключевыми словами',
   icon: FolderOpen,
   trend: metrics?.match_rate ? metrics.match_rate > 10 : false,
  },
  {
   title: 'Активные ключевые слова',
   value: stats.active_keywords.toString(),
   description: `из ${stats.total_keywords} всего`,
   icon: Hash,
   trend: stats.active_keywords > 0,
  },
  {
   title: 'Всего комментариев',
   value: stats.total_comments.toLocaleString(),
   description: `${stats.comments_with_keywords} с ключевыми словами`,
   icon: Calendar,
   trend: stats.comments_with_keywords > 0,
  },
 ]

 return (
  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
   {statCards.map((card, index) => {
    const Icon = card.icon
    const TrendIcon = getTrendIcon(card.trend)

    return (
     <Card key={index} className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
       <CardTitle className="text-sm font-medium">
        {card.title}
       </CardTitle>
       <div className="flex items-center gap-2">
        {TrendIcon && card.trendValue !== undefined && (
         <Badge
          variant={getTrendVariant(card.trend)}
          className="text-xs px-1.5 py-0.5"
         >
          <TrendIcon className="h-3 w-3 mr-1" />
          {Math.abs(card.trendValue).toFixed(0)}
         </Badge>
        )}
        <Icon className="h-4 w-4 text-muted-foreground" />
       </div>
      </CardHeader>
      <CardContent>
       <div className="text-2xl font-bold">{card.value}</div>
       <p className="text-xs text-muted-foreground">
        {card.description}
       </p>
      </CardContent>
     </Card>
    )
   })}
  </div>
 )
}
