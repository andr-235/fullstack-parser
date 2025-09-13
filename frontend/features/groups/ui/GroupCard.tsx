'use client'

import { useState } from 'react'

import { formatDistanceToNow } from 'date-fns'
import {
  Users,
  MessageSquare,
  Settings,
  Trash2,
  Edit,
  ExternalLink,
  Power,
  PowerOff,
  MoreHorizontal,
  Calendar,
  Hash,
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/shared/ui'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/ui'

import { VKGroup } from '@/entities/groups'

import { GroupForm } from '@/features/groups/ui/GroupForm'

interface GroupCardProps {
  group: VKGroup
  onUpdate?: (id: number, updates: any) => void
  onDelete?: (id: number) => void
  onToggleStatus?: (id: number, isActive: boolean) => void
}

interface GroupCardPropsWithHandlers extends GroupCardProps {
  onUpdate: (id: number, updates: any) => void
  onDelete: (id: number) => void
  onToggleStatus: (id: number, isActive: boolean) => void
}

export function GroupCard({ group, onUpdate, onDelete, onToggleStatus }: GroupCardProps) {
  const [showEditForm, setShowEditForm] = useState(false)

  const handleUpdate = async (updates: any) => {
    if (onUpdate) {
      try {
        await onUpdate(group.id, updates)
        setShowEditForm(false)
      } catch (err) {
        console.error('Failed to update group:', err)
      }
    }
  }

  const handleDelete = async () => {
    if (onDelete && confirm('Вы уверены, что хотите удалить эту группу?')) {
      try {
        await onDelete(group.id)
      } catch (err) {
        console.error('Failed to delete group:', err)
      }
    }
  }

  const handleToggleStatus = async () => {
    if (onToggleStatus) {
      try {
        await onToggleStatus(group.id, !group.is_active)
      } catch (err) {
        console.error('Failed to toggle group status:', err)
      }
    }
  }

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {group.photo_url ? (
              <img
                src={group.photo_url}
                alt={group.name}
                className="h-10 w-10 rounded-full object-cover"
              />
            ) : (
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                <Users className="h-5 w-5 text-primary" />
              </div>
            )}
            <div className="min-w-0 flex-1">
              <CardTitle className="text-sm font-medium truncate">{group.name}</CardTitle>
              <p className="text-xs text-muted-foreground">@{group.screen_name}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant={group.is_active ? 'default' : 'secondary'} className="text-xs">
              {group.is_active ? 'Активная' : 'Неактивная'}
            </Badge>

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
                    {group.is_active ? (
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
                  <DropdownMenuItem onClick={handleDelete} className="text-destructive">
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
              {group.total_comments_found.toLocaleString()} комментариев
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">
              {group.members_count?.toLocaleString() || 'Н/Д'} участников
            </span>
          </div>
        </div>

        {/* Last Parsed */}
        {group.last_parsed_at && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="h-3 w-3" />
            Последний парсинг{' '}
            {formatDistanceToNow(new Date(group.last_parsed_at), { addSuffix: true })}
          </div>
        )}

        {/* Description */}
        {group.description && (
          <p className="text-xs text-muted-foreground line-clamp-2">{group.description}</p>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => window.open(`https://vk.com/${group.screen_name}`, '_blank')}
          >
            <ExternalLink className="mr-2 h-3 w-3" />
            Открыть в VK
          </Button>

          <Button variant="outline" size="sm">
            <Hash className="h-3 w-3" />
          </Button>
        </div>
      </CardContent>

      {/* Edit Dialog */}
      {showEditForm && (
        <Dialog open={showEditForm} onOpenChange={setShowEditForm}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Редактировать группу</DialogTitle>
            </DialogHeader>
            <GroupForm
              initialData={{
                screen_name: group.screen_name,
                name: group.name,
                description: group.description,
                is_active: group.is_active,
                max_posts_to_check: group.max_posts_to_check,
              }}
              onSubmit={handleUpdate}
              onCancel={() => setShowEditForm(false)}
              submitLabel="Обновить группу"
            />
          </DialogContent>
        </Dialog>
      )}
    </Card>
  )
}
