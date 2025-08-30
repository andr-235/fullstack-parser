'use client'

import { Comment } from '@/entities/comment'
import { formatDistanceToNow } from 'date-fns'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Avatar, AvatarFallback } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'
import { Edit, Trash2, ThumbsUp, MessageCircle, MoreHorizontal } from 'lucide-react'
import {
 DropdownMenu,
 DropdownMenuContent,
 DropdownMenuItem,
 DropdownMenuTrigger,
} from '@/shared/ui'

interface CommentsListProps {
 comments: Comment[]
 loading?: boolean
 onEdit?: (comment: Comment) => void
 onDelete?: (commentId: string) => void
 onMarkViewed?: (commentId: string) => void
 onLike?: (commentId: string) => void
}

export function CommentsList({ comments, loading, onEdit, onDelete, onMarkViewed, onLike }: CommentsListProps) {
 if (loading) {
  return (
   <div className="space-y-4">
    {[...Array(3)].map((_, i) => (
     <Card key={i}>
      <CardHeader>
       <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-8 w-8" />
       </div>
      </CardHeader>
      <CardContent>
       <Skeleton className="h-4 w-full mb-2" />
       <Skeleton className="h-4 w-3/4" />
      </CardContent>
     </Card>
    ))}
   </div>
  )
 }

 if (comments.length === 0) {
  return (
   <Card>
    <CardContent className="py-12">
     <div className="text-center space-y-2">
      <MessageCircle className="mx-auto h-12 w-12 text-muted-foreground" />
      <p className="text-muted-foreground">Комментариев пока нет</p>
      <p className="text-sm text-muted-foreground">
       Будьте первым, кто оставит комментарий!
      </p>
     </div>
    </CardContent>
   </Card>
  )
 }

 return (
  <div className="space-y-4">
   {comments.map((comment) => (
    <Card key={comment.id} className="group hover:shadow-md transition-shadow">
     <CardHeader className="pb-3">
      <div className="flex items-start justify-between">
       <div className="flex items-center gap-3">
        <Avatar className="h-8 w-8">
         {comment.author_photo_url ? (
          <img
           src={comment.author_photo_url}
           alt={comment.author_name || 'Author'}
           className="h-8 w-8 rounded-full object-cover"
          />
         ) : (
          <AvatarFallback>
           {(comment.author_name || comment.author_screen_name || 'U').charAt(0).toUpperCase()}
          </AvatarFallback>
         )}
        </Avatar>
        <div>
         <CardTitle className="text-sm font-medium">
          {comment.author_name || comment.author_screen_name || 'Неизвестный автор'}
         </CardTitle>
         <p className="text-xs text-muted-foreground">
          {comment.published_at ? formatDistanceToNow(new Date(comment.published_at), { addSuffix: true }) : 'Дата неизвестна'}
         </p>
        </div>
       </div>

       <div className="flex items-center gap-2">
        <div className="flex gap-1">
         <Badge
          variant={comment.is_viewed ? 'default' : 'secondary'}
          className="text-xs"
         >
          {comment.is_viewed ? 'Просмотрено' : 'Новое'}
         </Badge>
         {comment.is_archived && (
          <Badge variant="outline" className="text-xs">
           Архивировано
          </Badge>
         )}
         {comment.matched_keywords_count > 0 && (
          <Badge variant="destructive" className="text-xs">
           {comment.matched_keywords_count} ключевых слов
          </Badge>
         )}
        </div>

        <DropdownMenu>
         <DropdownMenuTrigger asChild>
          <Button
           variant="ghost"
           size="sm"
           className="opacity-0 group-hover:opacity-100 transition-opacity"
          >
           <MoreHorizontal className="h-4 w-4" />
          </Button>
         </DropdownMenuTrigger>
         <DropdownMenuContent align="end">
          {!comment.is_viewed && onMarkViewed && (
           <DropdownMenuItem onClick={() => onMarkViewed(comment.id.toString())}>
            <Edit className="mr-2 h-4 w-4" />
            Отметить как просмотренное
           </DropdownMenuItem>
          )}
          {onDelete && (
           <DropdownMenuItem
            onClick={() => onDelete(comment.id.toString())}
            className="text-destructive"
           >
            <Trash2 className="mr-2 h-4 w-4" />
            Удалить
           </DropdownMenuItem>
          )}
         </DropdownMenuContent>
        </DropdownMenu>
       </div>
      </div>
     </CardHeader>

     <CardContent className="pt-0">
      <div className="space-y-3">
       <p className="text-sm leading-relaxed">{comment.text}</p>

       {comment.matched_keywords && comment.matched_keywords.length > 0 && (
        <div className="flex flex-wrap gap-1">
         {comment.matched_keywords.map((keyword, index) => (
          <Badge key={index} variant="outline" className="text-xs">
           {keyword}
          </Badge>
         ))}
        </div>
       )}

       <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
         {onLike && (
          <Button
           variant="ghost"
           size="sm"
           onClick={() => onLike(comment.id.toString())}
           className="text-muted-foreground hover:text-foreground"
          >
           <ThumbsUp className="mr-1 h-4 w-4" />
           {comment.likes_count}
          </Button>
         )}

         {comment.parent_comment_id && (
          <Badge variant="outline" className="text-xs">
           Ответ на #{comment.parent_comment_id}
          </Badge>
         )}

         {comment.group && (
          <Badge variant="outline" className="text-xs">
           {comment.group.name}
          </Badge>
         )}
        </div>

        <div className="text-xs text-muted-foreground">
         <p>VK ID: {comment.vk_id}</p>
         {comment.post_vk_id && <p>Пост: {comment.post_vk_id}</p>}
        </div>
       </div>
      </div>
     </CardContent>
    </Card>
   ))}
  </div>
 )
}
