'use client'

import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { VKCommentResponse } from '@/types/api'
import { Comment } from '@/entities/comment'

interface CommentsTableProps {
 comments: VKCommentResponse[]
 onMarkAsViewed?: (commentId: number) => void
 onArchive?: (commentId: number) => void
 onUnarchive?: (commentId: number) => void
 isLoading?: boolean
}

export function CommentsTable({
 comments,
 onMarkAsViewed,
 onArchive,
 onUnarchive,
 isLoading = false,
}: CommentsTableProps) {
 if (isLoading) {
  return (
   <div className="space-y-4">
    {Array.from({ length: 5 }).map((_, i) => (
     <div key={i} className="animate-pulse">
      <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-slate-700 rounded w-1/2"></div>
     </div>
    ))}
   </div>
  )
 }

 return (
  <Table>
   <TableHeader>
    <TableRow>
     <TableHead>Автор</TableHead>
     <TableHead>Комментарий</TableHead>
     <TableHead>Ключевые слова</TableHead>
     <TableHead>Дата</TableHead>
     <TableHead>Статус</TableHead>
     <TableHead>Действия</TableHead>
    </TableRow>
   </TableHeader>
   <TableBody>
    {comments.map((comment) => {
     const commentModel = new Comment(comment)

     return (
      <TableRow key={comment.id}>
       <TableCell>
        <div className="flex items-center space-x-2">
         <Avatar className="h-8 w-8">
          <AvatarImage src={comment.author_photo_url} />
          <AvatarFallback>
           {comment.author_name?.charAt(0) || 'U'}
          </AvatarFallback>
         </Avatar>
         <div>
          <div className="font-medium">{comment.author_name || 'Аноним'}</div>
          <div className="text-sm text-slate-400">ID: {comment.author_id}</div>
         </div>
        </div>
       </TableCell>
       <TableCell>
        <div className="max-w-md">
         <p className="text-sm text-slate-200 line-clamp-3">
          {comment.text}
         </p>
        </div>
       </TableCell>
       <TableCell>
        <div className="flex flex-wrap gap-1">
         {comment.matched_keywords?.map((keyword, index) => (
          <Badge key={index} variant="secondary" className="text-xs">
           {keyword}
          </Badge>
         ))}
        </div>
       </TableCell>
       <TableCell>
        <div className="text-sm text-slate-400">
         {formatDistanceToNow(new Date(comment.published_at), {
          addSuffix: true,
          locale: ru,
         })}
        </div>
       </TableCell>
       <TableCell>
        <Badge
         variant={
          commentModel.status === 'new'
           ? 'default'
           : commentModel.status === 'viewed'
            ? 'secondary'
            : 'destructive'
         }
        >
         {commentModel.status === 'new' && 'Новый'}
         {commentModel.status === 'viewed' && 'Просмотрен'}
         {commentModel.status === 'archived' && 'Архив'}
        </Badge>
       </TableCell>
       <TableCell>
        <div className="flex space-x-2">
         {onMarkAsViewed && !commentModel.isViewed && (
          <button
           onClick={() => onMarkAsViewed(comment.id)}
           className="text-blue-400 hover:text-blue-300 text-sm"
          >
           Отметить просмотренным
          </button>
         )}
         {onArchive && !commentModel.isArchived && (
          <button
           onClick={() => onArchive(comment.id)}
           className="text-orange-400 hover:text-orange-300 text-sm"
          >
           В архив
          </button>
         )}
         {onUnarchive && commentModel.isArchived && (
          <button
           onClick={() => onUnarchive(comment.id)}
           className="text-green-400 hover:text-green-300 text-sm"
          >
           Из архива
          </button>
         )}
        </div>
       </TableCell>
      </TableRow>
     )
    })}
   </TableBody>
  </Table>
 )
} 