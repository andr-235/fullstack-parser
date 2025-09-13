'use client'

import { useState } from 'react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { InfiniteScroll } from '@/shared/ui'

import { CommentFilters } from '@/features/comments/ui/CommentFilters'
import { CommentsList } from '@/features/comments/ui/CommentsList'
import { 
  useComments, 
  useDeleteComment, 
  useUpdateComment,
  type CommentFilter 
} from '@/features/comments'

export function CommentsPage() {
  const [filters, setFilters] = useState<CommentFilter>({
    search_text: '',
    is_deleted: false,
  })

  const { data, isLoading, error, refetch } = useComments({
    ...filters,
    include_author: true,
    limit: 20,
    offset: 0,
  })

  const deleteCommentMutation = useDeleteComment()
  const updateCommentMutation = useUpdateComment()

  const handleMarkAsViewed = async (id: string) => {
    try {
      await updateCommentMutation.mutateAsync({
        commentId: parseInt(id),
        data: { is_deleted: false }
      })
    } catch (err) {
      console.error('Error marking comment as viewed:', err)
    }
  }

  const handleDeleteComment = async (id: string) => {
    try {
      await deleteCommentMutation.mutateAsync(parseInt(id))
    } catch (err) {
      console.error('Error deleting comment:', err)
    }
  }

  const handleFiltersChange = (newFilters: CommentFilter) => {
    setFilters(newFilters)
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Комментарии VK</h1>
          <p className="text-muted-foreground">
            Мониторинг и управление комментариями из групп VK
            {data?.total && ` • ${data.total} комментариев`}
            {filters.search_text && (
              <span className="ml-2 text-blue-600 font-medium">(поиск: "{filters.search_text}")</span>
            )}
          </p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Фильтры</CardTitle>
        </CardHeader>
        <CardContent>
          <CommentFilters filters={filters} onFiltersChange={handleFiltersChange} />
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="py-4">
            <p className="text-destructive">
              Ошибка:{' '}
              {typeof error === 'string'
                ? error
                : typeof error === 'object' && error !== null
                  ? (error as { message?: string; detail?: string }).message ||
                    (error as { message?: string; detail?: string }).detail ||
                    JSON.stringify(error)
                  : String(error)}
            </p>
            <Button variant="outline" size="sm" onClick={refetch} className="mt-2">
              Попробовать снова
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Comments List */}
      <CommentsList
        comments={data?.items || []}
        loading={isLoading}
        onMarkViewed={handleMarkAsViewed}
        onDelete={handleDeleteComment}
      />
    </div>
  )
}
