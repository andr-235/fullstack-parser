'use client'

import React, { useState, useMemo } from 'react'
import {
  useInfiniteComments,
  useMarkCommentAsViewed,
  useArchiveComment,
  useUnarchiveComment,
} from '@/entities/comment'
import {
  useBulkMarkAsViewed,
  useBulkArchive,
  useBulkUnarchive,
  useBulkDelete,
} from '@/entities/comment'
import { useGroups } from '@/entities/group'
import { useKeywords } from '@/entities/keyword'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { ChevronDown, ChevronUp, MessageSquare } from 'lucide-react'
import {
  CommentsFilters,
  CommentsList,
  CommentsStats,
  CommentsBulkActions,
  CommentsSorting,
  type SortField,
  type SortOrder,
} from './components'
import type { VKCommentResponse } from '@/shared/types'

export default function CommentsPageEnhanced() {
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

  // Состояние сортировки
  const [sorting, setSorting] = useState<{
    field: SortField
    order: SortOrder
  }>({
    field: 'published_at',
    order: 'desc',
  })

  // Состояние выбранных комментариев
  const [selectedComments, setSelectedComments] = useState<number[]>([])

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

    // Добавляем сортировку
    params.order_by = sorting.field
    params.order_dir = sorting.order

    return params
  }, [filters, sorting])

  // Получение комментариев
  const {
    data: commentsData,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    refetch,
  } = useInfiniteComments(apiFilters)

  // Мутации для одиночных операций
  const markAsViewedMutation = useMarkCommentAsViewed()
  const archiveMutation = useArchiveComment()
  const unarchiveMutation = useUnarchiveComment()

  // Мутации для массовых операций
  const bulkMarkAsViewed = useBulkMarkAsViewed()
  const bulkArchive = useBulkArchive()
  const bulkUnarchive = useBulkUnarchive()
  const bulkDelete = useBulkDelete()

  // Обработчики одиночных операций
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

  // Обработчики массовых операций
  const handleBulkMarkAsViewed = async () => {
    if (selectedComments.length === 0) return
    await bulkMarkAsViewed.mutateAsync(selectedComments)
    setSelectedComments([])
  }

  const handleBulkArchive = async () => {
    if (selectedComments.length === 0) return
    await bulkArchive.mutateAsync(selectedComments)
    setSelectedComments([])
  }

  const handleBulkUnarchive = async () => {
    if (selectedComments.length === 0) return
    await bulkUnarchive.mutateAsync(selectedComments)
    setSelectedComments([])
  }

  const handleBulkDelete = async () => {
    if (selectedComments.length === 0) return
    if (confirm(`Удалить ${selectedComments.length} комментариев?`)) {
      await bulkDelete.mutateAsync(selectedComments)
      setSelectedComments([])
    }
  }

  // Обработчики выбора
  const handleSelectAll = () => {
    const allComments = commentsData?.pages?.flatMap((page) => page.items) || []
    setSelectedComments(allComments.map((comment) => comment.id))
  }

  const handleDeselectAll = () => {
    setSelectedComments([])
  }

  const handleCommentSelect = (commentId: number, selected: boolean) => {
    if (selected) {
      setSelectedComments((prev) => [...prev, commentId])
    } else {
      setSelectedComments((prev) => prev.filter((id) => id !== commentId))
    }
  }

  // Обработчики фильтров и сортировки
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

  const handleSortChange = (field: SortField, order: SortOrder) => {
    setSorting({ field, order })
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
  const isProcessing =
    bulkMarkAsViewed.isPending ||
    bulkArchive.isPending ||
    bulkUnarchive.isPending ||
    bulkDelete.isPending

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

      {/* Массовые действия */}
      <CommentsBulkActions
        selectedComments={selectedComments}
        totalComments={stats.total}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        onMarkAsViewed={handleBulkMarkAsViewed}
        onMarkAsUnviewed={() => {}} // TODO: Добавить
        onArchive={handleBulkArchive}
        onUnarchive={handleBulkUnarchive}
        onDelete={handleBulkDelete}
        isProcessing={isProcessing}
      />

      {/* Фильтры и сортировка */}
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
          <CardContent className="space-y-4">
            <CommentsFilters
              groups={groupsData?.items || []}
              keywords={keywordsData?.items || []}
              filters={filters}
              onFiltersChange={setFilters}
              onReset={handleResetFilters}
            />

            <div className="border-t border-slate-700 pt-4">
              <CommentsSorting
                sortField={sorting.field}
                sortOrder={sorting.order}
                onSortChange={handleSortChange}
              />
            </div>
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
        selectedComments={selectedComments}
        onCommentSelect={handleCommentSelect}
      />
    </div>
  )
}
