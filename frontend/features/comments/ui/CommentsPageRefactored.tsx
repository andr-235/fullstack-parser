'use client'

import React, { useState, useMemo } from 'react'
import {
  useInfiniteComments,
  useMarkCommentAsViewed,
  useArchiveComment,
  useUnarchiveComment,
} from '@/entities/comment'
import { useGroups } from '@/entities/group'
import { useKeywords } from '@/entities/keyword'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { ChevronDown, ChevronUp, MessageSquare } from 'lucide-react'
import { CommentsFilters, CommentsList, CommentsStats } from './components'
import type { VKCommentResponse } from '@/types/api'

export default function CommentsPage() {
  // Состояние фильтров
  const [filters, setFilters] = useState({
    text: '',
    groupId: null as number | null,
    keywordId: null as number | null,
    authorScreenName: [] as string[],
    dateFrom: '',
    dateTo: '',
    status: '',
  })

  // Состояние UI
  const [showFilters, setShowFilters] = useState(true)
  const [loadingComments, setLoadingComments] = useState<
    Record<string, boolean>
  >({})

  // Получение данных
  const { data: groupsData } = useGroups({ active_only: true })
  const { data: keywordsData } = useKeywords({ active_only: true })

  // Преобразование фильтров для API
  const apiFilters = useMemo(() => {
    const params: any = {}

    if (filters.text) params.text = filters.text
    if (filters.groupId) params.group_id = filters.groupId
    if (filters.keywordId) params.keyword_id = filters.keywordId
    if (filters.authorScreenName.length > 0)
      params.author_screen_name = filters.authorScreenName
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo

    if (filters.status === 'new') params.is_viewed = false
    if (filters.status === 'viewed') params.is_viewed = true
    if (filters.status === 'archived') params.is_archived = true

    return params
  }, [filters])

  // Получение комментариев
  const {
    data: commentsData,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    refetch,
  } = useInfiniteComments(apiFilters)

  // Мутации
  const markAsViewedMutation = useMarkCommentAsViewed()
  const archiveMutation = useArchiveComment()
  const unarchiveMutation = useUnarchiveComment()

  // Обработчики
  const handleMarkAsViewed = async (commentId: number) => {
    setLoadingComments((prev) => ({ ...prev, [`view-${commentId}`]: true }))
    try {
      await markAsViewedMutation.mutateAsync(commentId)
    } finally {
      setLoadingComments((prev) => ({ ...prev, [`view-${commentId}`]: false }))
    }
  }

  const handleArchiveComment = async (commentId: number) => {
    setLoadingComments((prev) => ({ ...prev, [`archive-${commentId}`]: true }))
    try {
      await archiveMutation.mutateAsync(commentId)
    } finally {
      setLoadingComments((prev) => ({
        ...prev,
        [`archive-${commentId}`]: false,
      }))
    }
  }

  const handleUnarchiveComment = async (commentId: number) => {
    setLoadingComments((prev) => ({
      ...prev,
      [`unarchive-${commentId}`]: true,
    }))
    try {
      await unarchiveMutation.mutateAsync(commentId)
    } finally {
      setLoadingComments((prev) => ({
        ...prev,
        [`unarchive-${commentId}`]: false,
      }))
    }
  }

  const handleResetFilters = () => {
    setFilters({
      text: '',
      groupId: null,
      keywordId: null,
      authorScreenName: [],
      dateFrom: '',
      dateTo: '',
      status: '',
    })
  }

  // Вычисление статистики
  const stats = useMemo(() => {
    if (!commentsData?.pages)
      return { total: 0, new: 0, viewed: 0, archived: 0, withKeywords: 0 }

    const allComments = commentsData.pages.flatMap((page) => page.items)

    return {
      total: allComments.length,
      new: allComments.filter((c) => !c.is_viewed && !c.is_archived).length,
      viewed: allComments.filter((c) => c.is_viewed && !c.is_archived).length,
      archived: allComments.filter((c) => c.is_archived).length,
      withKeywords: allComments.filter((c) => c.matched_keywords_count > 0)
        .length,
    }
  }, [commentsData])

  const allComments = commentsData?.pages?.flatMap((page) => page.items) || []

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Комментарии</h1>
          <p className="text-slate-400">Управление комментариями из VK групп</p>
        </div>
      </div>

      {/* Статистика */}
      <CommentsStats
        totalComments={stats.total}
        newComments={stats.new}
        viewedComments={stats.viewed}
        archivedComments={stats.archived}
        commentsWithKeywords={stats.withKeywords}
      />

      {/* Фильтры */}
      <Card>
        <CardHeader>
          <CardTitle
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => setShowFilters(!showFilters)}
          >
            <MessageSquare className="h-5 w-5" />
            Фильтры и поиск
            {showFilters ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </CardTitle>
        </CardHeader>
        {showFilters && (
          <CardContent>
            <CommentsFilters
              groups={groupsData?.items || []}
              keywords={keywordsData?.items || []}
              filters={filters}
              onFiltersChange={setFilters}
              onReset={handleResetFilters}
            />
          </CardContent>
        )}
      </Card>

      {/* Список комментариев */}
      <CommentsList
        comments={allComments}
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={hasNextPage || false}
        onMarkAsViewed={handleMarkAsViewed}
        onArchive={handleArchiveComment}
        onUnarchive={handleUnarchiveComment}
        onLoadMore={() => fetchNextPage()}
        onRefresh={() => refetch()}
      />
    </div>
  )
}
