'use client'

import React from 'react'
import { DataTable, type Column } from '@/shared/ui'
import { LoadingState, EmptyState, LoadingSpinner } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { RefreshCw, Archive, ArchiveRestore, Eye } from 'lucide-react'
import type { VKCommentResponse, VKGroupResponse } from '@/shared/types'

interface CommentsListProps {
  comments: VKCommentResponse[]
  isLoading: boolean
  isFetchingNextPage: boolean
  hasNextPage: boolean
  onMarkAsViewed: (commentId: number) => void
  onArchive: (commentId: number) => void
  onUnarchive: (commentId: number) => void
  onLoadMore: () => void
  onRefresh: () => void
  selectedComments?: number[]
  onCommentSelect?: (commentId: number, selected: boolean) => void
}

export function CommentsList({
  comments,
  isLoading,
  isFetchingNextPage,
  hasNextPage,
  onMarkAsViewed,
  onArchive,
  onUnarchive,
  onLoadMore,
  onRefresh,
  selectedComments = [],
  onCommentSelect,
}: CommentsListProps) {
  if (isLoading) {
    return <LoadingState message="Загрузка комментариев..." />
  }

  if (comments.length === 0) {
    return (
      <EmptyState
        title="Комментарии не найдены"
        description="Пока нет комментариев для отображения"
        action={{
          label: 'Обновить',
          onClick: onRefresh,
          variant: 'outline',
        }}
      />
    )
  }

  const columns: Column<VKCommentResponse>[] = [
    {
      key: 'id',
      title: 'ID',
      width: '80px',
      render: (value) => <span className="text-sm text-muted-foreground">#{value}</span>,
    },
    {
      key: 'text',
      title: 'Комментарий',
      render: (value) => (
        <div className="max-w-md truncate" title={value}>
          {value || 'Без текста'}
        </div>
      ),
    },
    {
      key: 'author_name',
      title: 'Автор',
      width: '150px',
      render: (value) => <span className="font-medium">{value || 'Неизвестен'}</span>,
    },
    {
      key: 'group',
      title: 'Группа',
      width: '150px',
      render: (value: VKGroupResponse | undefined) => <span>{value?.name || 'Неизвестна'}</span>,
    },
    {
      key: 'created_at',
      title: 'Дата',
      width: '120px',
      render: (value) => new Date(value).toLocaleDateString('ru-RU'),
    },
    {
      key: 'id',
      title: 'Действия',
      width: '200px',
      render: (_, record) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onMarkAsViewed(record.id)}
            title="Отметить как просмотренный"
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onArchive(record.id)}
            title="Архивировать"
          >
            <Archive className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onUnarchive(record.id)}
            title="Разархивировать"
          >
            <ArchiveRestore className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <DataTable
        data={comments}
        columns={columns}
        loading={isLoading}
        rowSelection={{
          selectedRowKeys: selectedComments,
          onChange: (selectedRowKeys, selectedRows) => {
            // Handle selection changes if needed
          },
          getRowKey: (record) => record.id
        }}
        emptyText="Нет комментариев для отображения"
      />

      {hasNextPage && (
        <div className="flex justify-center">
          <Button
            onClick={onLoadMore}
            disabled={isFetchingNextPage}
            variant="outline"
          >
            {isFetchingNextPage ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Загрузка...
              </>
            ) : (
              'Загрузить еще'
            )}
          </Button>
        </div>
      )}
    </div>
  )
}
