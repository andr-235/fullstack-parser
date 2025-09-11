'use client'

import { useState } from 'react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { InfiniteScroll } from '@/shared/ui'

import { useInfiniteComments } from '@/entities/comment'
import { CommentFilters as CommentFiltersType } from '@/entities/comment'

import { CommentFilters } from '@/features/comments/ui/CommentFilters'
import { CommentsList } from '@/features/comments/ui/CommentsList'

export function CommentsPage() {
   const [filters, setFilters] = useState<CommentFiltersType>({
      has_keywords: true // По умолчанию показываем только комментарии с ключевыми словами
   })

   const {
      comments,
      loading,
      loadingMore,
      error,
      hasMore,
      totalCount,
      loadMore,
      refetch
   } = useInfiniteComments(filters)

   const handleMarkAsViewed = async (id: string) => {
      try {
         // Обновляем локально для быстрого отклика
         // В реальном приложении здесь должен быть API вызов
         console.log('Mark as viewed:', id)
         refetch()
      } catch (err) {
         throw err
      }
   }

   const handleDeleteComment = async (id: string) => {
      try {
         // В реальном приложении здесь должен быть API вызов
         console.log('Delete comment:', id)
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
                  {totalCount > 0 && ` • ${totalCount} комментариев`}
                  {filters.has_keywords && (
                     <span className="ml-2 text-blue-600 font-medium">
                        (только с ключевыми словами)
                     </span>
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
                     Ошибка: {typeof error === 'string' ? error :
                        typeof error === 'object' && error !== null ?
                           (error as { message?: string; detail?: string }).message ||
                           (error as { message?: string; detail?: string }).detail ||
                           JSON.stringify(error) :
                           String(error)}
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

         {/* Comments List with Infinite Scroll */}
         <InfiniteScroll
            hasMore={hasMore}
            loading={loadingMore}
            onLoadMore={loadMore}
         >
            <CommentsList
               comments={comments}
               loading={loading}
               onMarkViewed={handleMarkAsViewed}
               onDelete={handleDeleteComment}
            />
         </InfiniteScroll>
      </div>
   )
}
