'use client'

import React from 'react'
import { StatsGrid, StatsCard } from '@/shared/ui'
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
      color: 'blue' as const,
    },
    {
      title: 'Новые',
      value: newComments,
      icon: Eye,
      color: 'green' as const,
    },
    {
      title: 'Просмотренные',
      value: viewedComments,
      icon: Eye,
      color: 'yellow' as const,
    },
    {
      title: 'Архивные',
      value: archivedComments,
      icon: Archive,
      color: 'gray' as const,
    },
    {
      title: 'С ключевыми словами',
      value: commentsWithKeywords,
      icon: Target,
      color: 'red' as const,
      percentage: totalComments > 0 ? (commentsWithKeywords / totalComments) * 100 : 0,
    },
  ]

  return (
    <StatsGrid
      stats={stats}
      columns="grid-cols-1 md:grid-cols-2 lg:grid-cols-5"
    />
  )
}
