'use client'

import { useState } from 'react'
import {
  useGroups,
  useCreateGroup,
  useUpdateGroup,
  useDeleteGroup,
} from '@/hooks/use-groups'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Plus, Play, Pause, Trash2, Search } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { VKGroupResponse } from '@/types/api'

export default function GroupsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [newGroupUrl, setNewGroupUrl] = useState('')
  const { data: groupsData, isLoading, error } = useGroups()
  const createGroupMutation = useCreateGroup()
  const updateGroupMutation = useUpdateGroup()
  const deleteGroupMutation = useDeleteGroup()

  const handleAddGroup = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newGroupUrl.trim()) return
    createGroupMutation.mutate(
      {
        vk_id_or_screen_name: newGroupUrl,
        name: 'Pending...',
        screen_name: 'pending...',
        is_active: true,
        max_posts_to_check: 100,
      },
      { onSuccess: () => setNewGroupUrl('') }
    )
  }

  const filteredGroups =
    groupsData?.items?.filter(
      (group) =>
        group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        group.screen_name.toLowerCase().includes(searchTerm.toLowerCase())
    ) || []

  const renderContent = () => {
    if (isLoading && !groupsData) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner />
        </div>
      )
    }

    if (error) {
      return (
        <div className="text-center text-red-500 py-10">
          <p>Ошибка при загрузке групп.</p>
          <p className="text-sm text-slate-400 mt-2">
            {error instanceof Error ? error.message : String(error)}
          </p>
        </div>
      )
    }

    if (filteredGroups.length === 0) {
      return (
        <div className="text-center py-10">
          <p className="text-slate-400">
            {searchTerm ? 'Группы не найдены' : 'Нет добавленных групп'}
          </p>
        </div>
      )
    }

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">ID</TableHead>
            <TableHead>Название</TableHead>
            <TableHead>Статус</TableHead>
            <TableHead>Последний парсинг</TableHead>
            <TableHead className="text-right">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredGroups.map((group: VKGroupResponse) => (
            <TableRow key={group.id}>
              <TableCell className="font-medium">{group.vk_id}</TableCell>
              <TableCell>{group.name}</TableCell>
              <TableCell>
                <Badge variant={group.is_active ? 'success' : 'secondary'}>
                  {group.is_active ? 'Активна' : 'На паузе'}
                </Badge>
              </TableCell>
              <TableCell>
                {group.last_parsed_at
                  ? formatDistanceToNow(new Date(group.last_parsed_at), {
                      addSuffix: true,
                      locale: ru,
                    })
                  : 'Никогда'}
              </TableCell>
              <TableCell className="text-right">
                <Button
                  variant="ghost"
                  size="icon"
                  disabled={updateGroupMutation.isPending}
                  onClick={() =>
                    updateGroupMutation.mutate({
                      groupId: group.id,
                      data: { is_active: !group.is_active },
                    })
                  }
                >
                  {group.is_active ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="text-red-500 hover:text-red-400"
                  disabled={deleteGroupMutation.isPending}
                  onClick={() => deleteGroupMutation.mutate(group.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-bold">
          Управление VK Группами
        </CardTitle>
        <CardDescription className="text-xs">
          Добавляйте, настраивайте и управляйте группами для парсинга.
        </CardDescription>
        <div className="flex justify-between items-center pt-2 gap-2">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Поиск по названию..."
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <form
            onSubmit={handleAddGroup}
            className="flex w-full max-w-sm items-center gap-1"
          >
            <Input
              placeholder="https://vk.com/example или example"
              value={newGroupUrl}
              onChange={(e) => setNewGroupUrl(e.target.value)}
              disabled={createGroupMutation.isPending}
            />
            <Button type="submit" disabled={createGroupMutation.isPending}>
              {createGroupMutation.isPending ? (
                <LoadingSpinner className="h-4 w-4" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              <span className="ml-1">Добавить</span>
            </Button>
          </form>
        </div>
      </CardHeader>
      <CardContent className="pt-2">{renderContent()}</CardContent>
    </Card>
  )
}
