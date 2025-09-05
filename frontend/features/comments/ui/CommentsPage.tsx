'use client'

import { useState } from 'react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'

import { useComments } from '@/entities/comment'
import { CommentFilters as CommentFiltersType } from '@/entities/comment'

import { CommentFilters } from '@/features/comments/ui/CommentFilters'
import { CommentsList } from '@/features/comments/ui/CommentsList'

export function CommentsPage() {
 const [filters, setFilters] = useState<CommentFiltersType>({})

 const {
  comments,
  loading,
  error,
  updateComment,
  deleteComment,
  markAsViewed,
  refetch
 } = useComments(filters)

 const _handleUpdateComment = async (id: string, updates: { is_viewed?: boolean; is_archived?: boolean }) => {
  try {
   await updateComment(id, updates)
   refetch()
  } catch (err) {
   throw err
  }
 }

 const handleMarkAsViewed = async (id: string) => {
  try {
   await markAsViewed(id)
   refetch()
  } catch (err) {
   throw err
  }
 }

 const handleDeleteComment = async (id: string) => {
  try {
   await deleteComment(id)
   refetch()
  } catch (err) {
   throw err
  }
 }

 const handleFiltersChange = (newFilters: CommentFiltersType) => {
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
     </p>
    </div>
   </div>

   {/* Filters */}
   <Card>
    <CardHeader>
     <CardTitle className="text-lg">Фильтры</CardTitle>
    </CardHeader>
    <CardContent>
     <CommentFilters
      filters={filters}
      onFiltersChange={handleFiltersChange}
     />
    </CardContent>
   </Card>

   {/* Error State */}
   {error && (
    <Card className="border-destructive">
     <CardContent className="py-4">
      <p className="text-destructive">
       Ошибка: {typeof error === 'string' ? error : JSON.stringify(error)}
      </p>
      <Button
       variant="outline"
       size="sm"
       onClick={refetch}
       className="mt-2"
      >
       Попробовать снова
      </Button>
     </CardContent>
    </Card>
   )}

   {/* Comments List */}
   <CommentsList
    comments={comments}
    loading={loading}
    onMarkViewed={handleMarkAsViewed}
    onDelete={handleDeleteComment}
   />
  </div>
 )
}
