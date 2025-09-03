'use client'

import { useState } from 'react'
import { Keyword } from '@/entities/keywords'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/shared/ui'
import { KeywordForm } from '@/features/keywords/ui/KeywordForm'
import { formatDistanceToNow } from 'date-fns'
import {
 Hash,
 Settings,
 Trash2,
 Edit,
 Power,
 PowerOff,
 MoreHorizontal,
 Calendar,
 MessageSquare,
 Type,
 WholeWord
} from 'lucide-react'
import {
 DropdownMenu,
 DropdownMenuContent,
 DropdownMenuItem,
 DropdownMenuTrigger,
} from '@/shared/ui'

interface KeywordCardProps {
 keyword: Keyword
 onUpdate?: (id: number, updates: any) => void
 onDelete?: (id: number) => void
 onToggleStatus?: (id: number, isActive: boolean) => void
}

export function KeywordCard({ keyword, onUpdate, onDelete, onToggleStatus }: KeywordCardProps) {
 const [showEditForm, setShowEditForm] = useState(false)

 const handleUpdate = async (updates: any) => {
  if (onUpdate) {
   try {
    await onUpdate(keyword.id, updates)
    setShowEditForm(false)
   } catch (err) {
    console.error('Failed to update keyword:', err)
   }
  }
 }

 const handleDelete = async () => {
  if (onDelete && confirm('Вы уверены, что хотите удалить это ключевое слово?')) {
   try {
    await onDelete(keyword.id)
   } catch (err) {
    console.error('Failed to delete keyword:', err)
   }
  }
 }

 const handleToggleStatus = async () => {
  if (onToggleStatus) {
   try {
    await onToggleStatus(keyword.id, !keyword.status.is_active)
   } catch (err) {
    console.error('Failed to toggle keyword status:', err)
   }
  }
 }

 return (
  <Card className="group hover:shadow-md transition-shadow">
   <CardHeader className="pb-3">
    <div className="flex items-start justify-between">
     <div className="flex items-center gap-3">
      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10">
       <Hash className="h-5 w-5 text-primary" />
      </div>
      <div className="min-w-0 flex-1">
       <CardTitle className="text-sm font-medium truncate">
        "{keyword.word}"
       </CardTitle>
       <p className="text-xs text-muted-foreground">
        {keyword.category?.name || 'Без категории'}
       </p>
      </div>
     </div>

     <div className="flex items-center gap-2">
      <div className="flex gap-1">
       <Badge
        variant={keyword.status.is_active ? 'default' : 'secondary'}
        className="text-xs"
       >
        {keyword.status.is_active ? 'Активное' : 'Неактивное'}
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
        {onUpdate && (
         <DropdownMenuItem onClick={() => setShowEditForm(true)}>
          <Edit className="mr-2 h-4 w-4" />
          Редактировать
         </DropdownMenuItem>
        )}
        {onToggleStatus && (
         <DropdownMenuItem onClick={handleToggleStatus}>
          {keyword.status.is_active ? (
           <>
            <PowerOff className="mr-2 h-4 w-4" />
            Деактивировать
           </>
          ) : (
           <>
            <Power className="mr-2 h-4 w-4" />
            Активировать
           </>
          )}
         </DropdownMenuItem>
        )}
        {onDelete && (
         <DropdownMenuItem
          onClick={handleDelete}
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

   <CardContent className="pt-0 space-y-4">
    {/* Stats */}
    <div className="grid grid-cols-2 gap-4">
     <div className="flex items-center gap-2">
      <MessageSquare className="h-4 w-4 text-muted-foreground" />
      <span className="text-sm">
       {(keyword.total_matches || keyword.match_count || 0).toLocaleString()} совпадений
      </span>
     </div>

     <div className="flex items-center gap-2">
      <Calendar className="h-4 w-4 text-muted-foreground" />
      <span className="text-sm">
       {formatDistanceToNow(new Date(keyword.created_at), { addSuffix: true })}
      </span>
     </div>
    </div>

    {/* Description */}
    {keyword.description && (
     <p className="text-xs text-muted-foreground line-clamp-2">
      {keyword.description}
     </p>
    )}

    {/* Actions */}
    <div className="flex items-center gap-2 pt-2">
     <Button
      variant="outline"
      size="sm"
      className="flex-1"
      onClick={() => {
       // TODO: Navigate to keyword matches/comments
       console.log('Navigate to matches for keyword:', keyword.id)
      }}
     >
      <MessageSquare className="mr-2 h-3 w-3" />
      Показать совпадения
     </Button>

     <Button variant="outline" size="sm">
      <Settings className="h-3 w-3" />
     </Button>
    </div>
   </CardContent>

   {/* Edit Dialog */}
   {showEditForm && (
    <Dialog open={showEditForm} onOpenChange={setShowEditForm}>
     <DialogContent>
      <DialogHeader>
       <DialogTitle>Редактировать ключевое слово</DialogTitle>
      </DialogHeader>
      <KeywordForm
       initialData={{
        word: keyword.word || '',
        category: keyword.category?.name || '',
        description: keyword.description,
        is_active: keyword.status.is_active,
       }}
       onSubmit={handleUpdate}
       onCancel={() => setShowEditForm(false)}
       submitLabel="Обновить ключевое слово"
      />
     </DialogContent>
    </Dialog>
   )}
  </Card>
 )
}
