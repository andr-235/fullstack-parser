'use client'

import React from 'react'
import { CommentsTable } from '@/widgets/comments-table'
import { LoadingSpinner } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { RefreshCw } from 'lucide-react'
import type { VKCommentResponse } from '@/types/api'

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
    return (
      <div className="flex items-center justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (comments.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-slate-400">Комментарии не найдены</p>
        <Button onClick={onRefresh} variant="outline" className="mt-4">
          <RefreshCw className="h-4 w-4 mr-2" />
          Обновить
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <CommentsTable
        comments={comments}
        onMarkAsViewed={onMarkAsViewed}
        onArchive={onArchive}
        onUnarchive={onUnarchive}
        isLoading={isLoading}
        selectedComments={selectedComments}
        onCommentSelect={onCommentSelect || (() => { })}
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
