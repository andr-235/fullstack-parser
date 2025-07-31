'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { MessageSquare, Eye, Archive, Target } from 'lucide-react'

interface CommentsStatsProps {
  totalComments: number
  newComments: number
  viewedComments: number
  archivedComments: number
  commentsWithKeywords: number
}

export function CommentsStats({
  totalComments,
  newComments,
  viewedComments,
  archivedComments,
  commentsWithKeywords,
}: CommentsStatsProps) {
  const stats = [
    {
      title: 'Всего комментариев',
      value: totalComments,
      icon: MessageSquare,
      color: 'bg-blue-500',
    },
    {
      title: 'Новые',
      value: newComments,
      icon: Eye,
      color: 'bg-green-500',
    },
    {
      title: 'Просмотренные',
      value: viewedComments,
      icon: Eye,
      color: 'bg-yellow-500',
    },
    {
      title: 'Архивные',
      value: archivedComments,
      icon: Archive,
      color: 'bg-gray-500',
    },
    {
      title: 'С ключевыми словами',
      value: commentsWithKeywords,
      icon: Target,
      color: 'bg-red-500',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <Icon
                className={`h-4 w-4 ${stat.color} text-white p-1 rounded`}
              />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              {stat.title === 'С ключевыми словами' && totalComments > 0 && (
                <p className="text-xs text-slate-400">
                  {((commentsWithKeywords / totalComments) * 100).toFixed(1)}%
                  от общего
                </p>
              )}
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
