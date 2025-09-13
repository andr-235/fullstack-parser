'use client'

import { formatDistanceToNow } from 'date-fns'
import { Edit, Trash2, ThumbsUp, MessageCircle, MoreHorizontal } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Avatar, AvatarFallback } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/ui'
import { HighlightText } from '@/shared/ui'

import { CommentResponse } from '@/features/comments'
import { formatCommentDate, getAuthorFullName, getAuthorInitials } from '@/features/comments'

interface CommentsListProps {
  comments: CommentResponse[]
  loading?: boolean
  onEdit?: (comment: CommentResponse) => void
  onDelete?: (commentId: string) => void
  onMarkViewed?: (commentId: string) => void
  onLike?: (commentId: string) => void
}

export function CommentsList({
  comments,
  loading,
  onEdit: _onEdit,
  onDelete,
  onMarkViewed,
  onLike,
}: CommentsListProps) {
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
            <p className="text-sm text-muted-foreground">Будьте первым, кто оставит комментарий!</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {comments.map(comment => (
        <Card key={comment.id} className="group hover:shadow-md transition-shadow">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <Avatar className="h-8 w-8">
                  {comment.author?.photo_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={comment.author.photo_url}
                      alt={getAuthorFullName(comment.author)}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                  ) : (
                    <AvatarFallback>
                      {comment.author ? getAuthorInitials(comment.author) : 'U'}
                    </AvatarFallback>
                  )}
                </Avatar>
                <div>
                  <CardTitle className="text-sm font-medium">
                    {comment.author ? getAuthorFullName(comment.author) : 'Неизвестный автор'}
                  </CardTitle>
                  <p className="text-xs text-muted-foreground">
                    {formatCommentDate(comment.created_at)}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <Badge variant={comment.is_deleted ? 'destructive' : 'secondary'} className="text-xs">
                    {comment.is_deleted ? 'Удален' : 'Активен'}
                  </Badge>
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
                    {!comment.is_deleted && onMarkViewed && (
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
              <div className="text-sm leading-relaxed">
                {comment.text}
              </div>

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
                      0
                    </Button>
                  )}
                </div>

                <div className="text-xs text-muted-foreground">
                  <p>VK ID: {comment.vk_id}</p>
                  <p>Пост: {comment.post_id}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
