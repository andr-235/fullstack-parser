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
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { LoadingSpinnerWithText } from '@/components/ui/loading-spinner'
import {
  Plus,
  Users,
  Settings,
  Play,
  Pause,
  Trash2,
  ExternalLink,
  Search,
  Filter,
  AlertCircle,
} from 'lucide-react'
import { formatNumber, formatRelativeTime } from '@/lib/utils'
import type { VKGroupResponse } from '@/types/api'
import Link from 'next/link'

export default function GroupsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeOnly, setActiveOnly] = useState(false)
  const [newGroupUrl, setNewGroupUrl] = useState('')

  const {
    data: groupsData,
    isLoading,
    error,
  } = useGroups({
    active_only: activeOnly,
    limit: 50,
  })

  const createGroupMutation = useCreateGroup()
  const updateGroupMutation = useUpdateGroup()
  const deleteGroupMutation = useDeleteGroup()

  const groups = groupsData?.items || []
  const total = groupsData?.total || 0

  const filteredGroups = groups.filter(
    (group: VKGroupResponse) =>
      group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      group.screen_name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleToggleActive = (group: VKGroupResponse) => {
    updateGroupMutation.mutate({
      groupId: group.id,
      data: { is_active: !group.is_active },
    })
  }

  const handleDeleteGroup = (groupId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить эту группу?')) {
      deleteGroupMutation.mutate(groupId)
    }
  }

  const handleAddGroup = () => {
    if (!newGroupUrl.trim()) return
    createGroupMutation.mutate(
      {
        vk_id_or_screen_name: newGroupUrl,
        is_active: true,
        max_posts_to_check: 100, // default value
        name: 'Pending...', // will be updated by backend
        screen_name: 'Pending...', // will be updated by backend
      },
      {
        onSuccess: () => {
          setNewGroupUrl('')
        },
      }
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinnerWithText text="Загрузка групп..." size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center text-red-500">
          <AlertCircle className="mx-auto h-12 w-12" />
          <h3 className="mt-4 text-lg font-medium">Ошибка загрузки групп</h3>
          <p className="mt-1 text-sm text-gray-600">
            Не удалось загрузить список групп. Проверьте подключение к API.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">VK Группы</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Управление группами ВКонтакте для мониторинга и парсинга
            комментариев
          </p>
        </div>
      </div>

      {/* Add new group */}
      <Card>
        <CardHeader>
          <CardTitle>Добавить новую группу</CardTitle>
          <CardDescription>
            Вставьте ссылку или короткое имя (screen name) группы.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex w-full items-center space-x-2">
            <Input
              type="text"
              placeholder="https://vk.com/example или example"
              className="flex-1"
              value={newGroupUrl}
              onChange={(e) => setNewGroupUrl(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddGroup()}
            />
            <Button
              onClick={handleAddGroup}
              disabled={createGroupMutation.isPending}
            >
              {createGroupMutation.isPending ? (
                <LoadingSpinnerWithText text="" size="sm" />
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Добавить
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Всего групп</p>
                <p className="text-2xl font-bold">{formatNumber(total)}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Активных</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatNumber(
                    groups.filter((g: VKGroupResponse) => g.is_active).length
                  )}
                </p>
              </div>
              <Play className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Неактивных</p>
                <p className="text-2xl font-bold text-gray-500">
                  {formatNumber(
                    groups.filter((g: VKGroupResponse) => !g.is_active).length
                  )}
                </p>
              </div>
              <Pause className="h-8 w-8 text-gray-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  Всего комментариев
                </p>
                <p className="text-2xl font-bold text-purple-600">
                  {formatNumber(
                    groups.reduce(
                      (sum: number, g: VKGroupResponse) =>
                        sum + g.total_comments_found,
                      0
                    )
                  )}
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Поиск по названию или screen_name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={activeOnly}
                  onChange={(e) => setActiveOnly(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">Только активные</span>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Groups List */}
      {isLoading && filteredGroups.length === 0 ? (
        <div className="flex items-center justify-center min-h-[200px]">
          <LoadingSpinnerWithText text="Обновление..." size="md" />
        </div>
      ) : filteredGroups.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredGroups.map((group: VKGroupResponse) => (
            <Card
              key={group.id}
              className="hover:shadow-lg transition-shadow flex flex-col"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold">
                      <Link
                        href={`https://vk.com/${group.screen_name}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="hover:underline"
                      >
                        {group.name}
                      </Link>
                    </CardTitle>
                    <CardDescription className="flex items-center gap-1 mt-1">
                      @{group.screen_name}
                      <ExternalLink className="h-3 w-3" />
                    </CardDescription>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Badge variant={group.is_active ? 'success' : 'secondary'}>
                      {group.is_active ? 'Активна' : 'Неактивна'}
                    </Badge>
                    {group.is_closed && (
                      <Badge variant="warning">Закрытая</Badge>
                    )}
                  </div>
                </div>
              </CardHeader>

              <CardContent className="flex-grow space-y-3">
                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Участников</p>
                    <p className="font-semibold">
                      {group.members_count
                        ? formatNumber(group.members_count)
                        : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Постов проверено</p>
                    <p className="font-semibold">
                      {formatNumber(group.total_posts_parsed)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Комментариев найдено</p>
                    <p className="font-semibold">
                      {formatNumber(group.total_comments_found)}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Лимит постов</p>
                    <p className="font-semibold">
                      {formatNumber(group.max_posts_to_check)}
                    </p>
                  </div>
                </div>

                {/* Last parsed */}
                {group.last_parsed_at && (
                  <div className="text-sm">
                    <p className="text-gray-600">Последний парсинг</p>
                    <p className="font-medium">
                      {formatRelativeTime(group.last_parsed_at)}
                    </p>
                  </div>
                )}

                {/* Description */}
                {group.description && (
                  <div>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {group.description}
                    </p>
                  </div>
                )}
              </CardContent>
              {/* Actions */}
              <div className="p-4 pt-2 border-t mt-auto">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant={group.is_active ? 'secondary' : 'default'}
                      onClick={() => handleToggleActive(group)}
                      disabled={updateGroupMutation.isPending}
                    >
                      {group.is_active ? (
                        <>
                          <Pause className="h-4 w-4 mr-1" />
                          Остановить
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-1" />
                          Запустить
                        </>
                      )}
                    </Button>

                    <Button size="sm" variant="ghost">
                      <Settings className="h-4 w-4 mr-1" />
                      Настройки
                    </Button>
                  </div>

                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteGroup(group.id)}
                    disabled={deleteGroupMutation.isPending}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="col-span-full">
          <Card>
            <CardContent className="p-12">
              <div className="text-center">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Группы не найдены
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm
                    ? `Нет групп, соответствующих запросу "${searchTerm}"`
                    : 'Добавьте первую группу для начала мониторинга'}
                </p>
                <Button
                  onClick={() => document.querySelector('input')?.focus()}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Добавить группу
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
