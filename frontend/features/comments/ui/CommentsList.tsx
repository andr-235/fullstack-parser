'use client'

import { Comment } from '@/entities/comment'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { formatDistanceToNow } from 'date-fns'

interface CommentsListProps {
 comments: Comment[]
 loading?: boolean
 onEdit?: (comment: Comment) => void
 onDelete?: (commentId: string) => void
}

export function CommentsList({ comments, loading, onEdit, onDelete }: CommentsListProps) {
 if (loading) {
  return <div>Loading comments...</div>
 }

 if (comments.length === 0) {
  return (
   <Card>
    <CardContent className="py-8">
     <p className="text-center text-muted-foreground">No comments yet</p>
    </CardContent>
   </Card>
  )
 }

 return (
  <div className="space-y-4">
   {comments.map((comment) => (
    <Card key={comment.id}>
     <CardHeader className="pb-3">
      <div className="flex items-center justify-between">
       <CardTitle className="text-sm font-medium">
        Comment #{comment.id}
       </CardTitle>
       <div className="flex items-center gap-2">
        {onEdit && (
         <Button
          variant="outline"
          size="sm"
          onClick={() => onEdit(comment)}
         >
          Edit
         </Button>
        )}
        {onDelete && (
         <Button
          variant="destructive"
          size="sm"
          onClick={() => onDelete(comment.id.toString())}
         >
          Delete
         </Button>
        )}
       </div>
      </div>
     </CardHeader>
     <CardContent>
      <p className="text-sm text-muted-foreground mb-2">
       {formatDistanceToNow(new Date(comment.createdAt), { addSuffix: true })}
      </p>
      <p className="text-sm">{comment.content}</p>
      {comment.likes > 0 && (
       <p className="text-xs text-muted-foreground mt-2">
        {comment.likes} like{comment.likes !== 1 ? 's' : ''}
       </p>
      )}
     </CardContent>
    </Card>
   ))}
  </div>
 )
}
