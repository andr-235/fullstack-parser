'use client'

import { MessageSquare, Users, Hash, FolderOpen } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Skeleton } from '@/shared/ui'

import { VKGroup, UpdateGroupRequest } from '@/entities/groups'

import { GroupCard } from '@/features/groups/ui/GroupCard'

interface GroupsListProps {
  groups: VKGroup[]
  loading?: boolean
  totalGroups?: number
  totalActiveGroups?: number
  onUpdate?: (id: number, updates: UpdateGroupRequest) => void
  onDelete?: (id: number) => void
  onToggleStatus?: (id: number, isActive: boolean) => void
}

export function GroupsList({
  groups,
  loading,
  totalGroups,
  totalActiveGroups,
  onUpdate,
  onDelete,
  onToggleStatus,
}: GroupsListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <Skeleton className="h-6 w-48" />
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

  if (groups.length === 0) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center space-y-4">
            <Users className="mx-auto h-16 w-16 text-muted-foreground" />
            <div>
              <h3 className="text-lg font-medium">Группы не найдены</h3>
              <p className="text-muted-foreground">
                {loading
                  ? 'Загрузка групп...'
                  : 'Добавьте свою первую группу VK для начала мониторинга комментариев'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего групп</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalGroups !== undefined ? totalGroups.toLocaleString() : groups.length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Активные группы</CardTitle>
            <FolderOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalActiveGroups !== undefined
                ? totalActiveGroups.toLocaleString()
                : groups.filter(g => g.is_active).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Всего комментариев</CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {groups.reduce((sum, group) => sum + group.total_comments_found, 0).toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Среднее число участников</CardTitle>
            <Hash className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {groups.length > 0
                ? Math.round(
                    groups
                      .filter(g => g.members_count)
                      .reduce((sum, group) => sum + (group.members_count || 0), 0) /
                      groups.filter(g => g.members_count).length
                  ).toLocaleString()
                : '0'}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Groups Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {groups.map(group => (
          <GroupCard
            key={group.id}
            group={group}
            onUpdate={onUpdate || (() => {})}
            onDelete={onDelete || (() => {})}
            onToggleStatus={onToggleStatus || (() => {})}
          />
        ))}
      </div>
    </div>
  )
}
