'use client'

import React, { useState, useMemo } from 'react'
import {
  useInfiniteGroups,
  useUpdateGroup,
  useDeleteGroup,
  useRefreshGroupInfo,
} from '@/features/groups/hooks'
import { Card, CardContent } from '@/shared/ui'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { LoadingSpinner } from '@/shared/ui'
import {
  Play,
  Pause,
  Trash2,
  Users,
  MessageSquare,
  Settings,
  Copy,
  ExternalLink,
  Check,
  RefreshCw,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { VKGroupResponse } from '@/types/api'
import { toast } from 'react-hot-toast'
import { useDebounce, useInfiniteScroll } from '@/shared/hooks'
import {
  GroupsHeader,
  GroupsStatsComponent,
  GroupsManagement,
} from './components'
import { useQueryClient } from '@tanstack/react-query'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui/avatar'
import { format } from 'date-fns'

const AVATAR_PLACEHOLDER =
  'https://ui-avatars.com/api/?background=0D8ABC&color=fff&name='

export default function GroupsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeOnly, setActiveOnly] = useState(false)
  const [copiedGroup, setCopiedGroup] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<
    'comments' | 'members' | 'name' | 'last_parsed'
  >('comments')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const debouncedSearch = useDebounce(searchTerm, 500)

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteGroups({
    active_only: activeOnly,
    search: debouncedSearch,
  })

  const updateGroupMutation = useUpdateGroup()
  const deleteGroupMutation = useDeleteGroup()
  const refreshGroupMutation = useRefreshGroupInfo()
  const queryClient = useQueryClient()

  const groups = useMemo(() => {
    console.log('🔍 Данные от useInfiniteGroups:', data)
    console.log('🔍 Страницы данных:', data?.pages)

    const allGroups = data?.pages.flatMap((page) => page.items) ?? []
    console.log('🔍 Все группы после flatMap:', allGroups)

    return allGroups.sort((a, b) => {
      let aValue: any
      let bValue: any

      switch (sortBy) {
        case 'comments':
          aValue = a.total_comments_found || 0
          bValue = b.total_comments_found || 0
          break
        case 'members':
          aValue = a.members_count || 0
          bValue = b.members_count || 0
          break
        case 'name':
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          break
        case 'last_parsed':
          aValue = a.last_parsed_at ? new Date(a.last_parsed_at).getTime() : 0
          bValue = b.last_parsed_at ? new Date(b.last_parsed_at).getTime() : 0
          break
        default:
          return 0
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : aValue < bValue ? -1 : 0
      } else {
        return aValue < bValue ? 1 : aValue > bValue ? -1 : 0
      }
    })
  }, [data, sortBy, sortOrder])

  // Хук для автоматической загрузки при скролле
  const observerRef = useInfiniteScroll({
    hasNextPage,
    isFetchingNextPage,
    fetchNextPage,
    threshold: 200,
  })

  // Быстрое копирование ссылки с анимацией
  const handleCopyLink = async (screen_name: string) => {
    try {
      await navigator.clipboard.writeText(`https://vk.com/${screen_name}`)
      setCopiedGroup(screen_name)
      toast.success('Ссылка скопирована! 📋')

      // Сброс через 2 секунды
      setTimeout(() => setCopiedGroup(null), 2000)
    } catch (err) {
      toast.error('Не удалось скопировать ссылку')
    }
  }

  // Функция для переключения сортировки
  const handleSort = (field: typeof sortBy) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  // Статистика
  const totalGroups = data?.pages[0]?.total || 0
  const activeGroups = groups.filter((group) => group?.is_active).length
  const inactiveGroups = totalGroups - activeGroups

  return (
    <div className="space-y-4">
      {/* Заголовок */}
      <GroupsHeader />

      {/* Статистика */}
      <GroupsStatsComponent
        totalGroups={totalGroups}
        activeGroups={activeGroups}
        inactiveGroups={inactiveGroups}
      />

      {/* Управление группами */}
      <GroupsManagement
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        activeOnly={activeOnly}
        onActiveOnlyChange={setActiveOnly}
      />

      {/* Таблица групп */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
              <div className="relative">
                <LoadingSpinner className="h-8 w-8 text-blue-500" />
                <div className="absolute inset-0 rounded-full border-2 border-blue-200 animate-ping"></div>
              </div>
              <span className="text-slate-600 font-medium">
                Загрузка групп...
              </span>
            </div>
          ) : error ? (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
                <Trash2 className="h-8 w-8 text-red-500" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-2">
                Ошибка загрузки
              </h3>
              <p className="text-slate-600 mb-4">
                Не удалось загрузить список групп
              </p>
              <p className="text-sm text-slate-400">
                {error instanceof Error ? error.message : String(error)}
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gradient-to-r from-slate-700 to-slate-600 shadow-md hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600">
                      <TableHead className="text-slate-200 text-xs font-bold whitespace-nowrap">
                        ID
                      </TableHead>
                      <TableHead className="text-slate-200 text-xs font-bold w-80 max-w-80">
                        <div
                          className="flex items-center gap-2 cursor-pointer hover:bg-slate-600 transition-colors select-none"
                          onClick={() => handleSort('name')}
                        >
                          Группа
                          <div className="flex flex-col">
                            {sortBy === 'name' ? (
                              sortOrder === 'asc' ? (
                                <ArrowUp className="h-3 w-3 text-blue-400" />
                              ) : (
                                <ArrowDown className="h-3 w-3 text-blue-400" />
                              )
                            ) : (
                              <ArrowUpDown className="h-3 w-3 text-slate-400" />
                            )}
                          </div>
                        </div>
                      </TableHead>
                      <TableHead className="text-slate-200 text-xs font-bold whitespace-nowrap">
                        Статус
                      </TableHead>
                      <TableHead className="text-slate-200 text-xs font-bold whitespace-nowrap">
                        <div
                          className="flex items-center gap-2 cursor-pointer hover:bg-slate-600 transition-colors select-none"
                          onClick={() => handleSort('comments')}
                        >
                          Комментарии
                          <div className="flex flex-col">
                            {sortBy === 'comments' ? (
                              sortOrder === 'asc' ? (
                                <ArrowUp className="h-3 w-3 text-blue-400" />
                              ) : (
                                <ArrowDown className="h-3 w-3 text-blue-400" />
                              )
                            ) : (
                              <ArrowUpDown className="h-3 w-3 text-slate-400" />
                            )}
                          </div>
                        </div>
                      </TableHead>
                      <TableHead className="text-slate-200 text-xs font-bold whitespace-nowrap">
                        <div
                          className="flex items-center gap-2 cursor-pointer hover:bg-slate-600 transition-colors select-none"
                          onClick={() => handleSort('members')}
                        >
                          Участники
                          <div className="flex flex-col">
                            {sortBy === 'members' ? (
                              sortOrder === 'asc' ? (
                                <ArrowUp className="h-3 w-3 text-blue-400" />
                              ) : (
                                <ArrowDown className="h-3 w-3 text-blue-400" />
                              )
                            ) : (
                              <ArrowUpDown className="h-3 w-3 text-slate-400" />
                            )}
                          </div>
                        </div>
                      </TableHead>
                      <TableHead className="text-slate-200 text-xs font-bold whitespace-nowrap">
                        <div
                          className="flex items-center gap-2 cursor-pointer hover:bg-slate-600 transition-colors select-none"
                          onClick={() => handleSort('last_parsed')}
                        >
                          Последний парсинг
                          <div className="flex flex-col">
                            {sortBy === 'last_parsed' ? (
                              sortOrder === 'asc' ? (
                                <ArrowUp className="h-3 w-3 text-blue-400" />
                              ) : (
                                <ArrowDown className="h-3 w-3 text-blue-400" />
                              )
                            ) : (
                              <ArrowUpDown className="h-3 w-3 text-slate-400" />
                            )}
                          </div>
                        </div>
                      </TableHead>
                      <TableHead className="text-slate-200 text-xs font-bold text-right whitespace-nowrap">
                        Действия
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {groups.map((group) => (
                      <TableRow
                        key={group?.id}
                        className="group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01]"
                      >
                        <TableCell className="font-mono text-xs text-slate-400">
                          {group?.vk_id}
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="relative">
                              <Avatar className="w-10 h-10 border border-slate-600">
                                <AvatarImage
                                  src={
                                    group?.photo_url ||
                                    `${AVATAR_PLACEHOLDER}${encodeURIComponent(group?.name || '')}`
                                  }
                                  alt={group?.name}
                                  loading="lazy"
                                />
                                {group?.is_active && (
                                  <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full border border-slate-800 animate-pulse"></div>
                                )}
                                <AvatarFallback className="bg-slate-700 text-slate-300">
                                  {group?.name?.charAt(0)?.toUpperCase() || 'G'}
                                </AvatarFallback>
                              </Avatar>
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-slate-200 truncate">
                                {group?.name}
                              </div>
                              <div className="text-xs text-slate-400">
                                @{group?.screen_name}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={
                                group?.is_active ? 'default' : 'secondary'
                              }
                              className={`${group?.is_active
                                ? 'bg-green-600 hover:bg-green-700'
                                : 'bg-slate-600 hover:bg-slate-700'
                                } text-white`}
                            >
                              {group?.is_active ? 'Активна' : 'Неактивна'}
                            </Badge>
                          </div>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="font-mono text-sm text-slate-300">
                            {group?.total_comments_found?.toLocaleString() ||
                              '0'}
                          </span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="font-mono text-sm text-slate-300">
                            {group?.members_count?.toLocaleString() || 'N/A'}
                          </span>
                        </TableCell>
                        <TableCell className="text-center">
                          <span className="text-xs text-slate-400">
                            {group?.last_parsed_at ? (
                              format(
                                new Date(group?.last_parsed_at),
                                'dd.MM.yyyy HH:mm',
                                { locale: ru }
                              )
                            ) : (
                              'Никогда'
                            )}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() =>
                                refreshGroupMutation.mutate(group?.id || 0, {
                                  onSuccess: () => {
                                    toast.success('Группа обновлена')
                                    queryClient.invalidateQueries({
                                      queryKey: ['groups'],
                                    })
                                  },
                                  onError: (error) => {
                                    toast.error(
                                      `Ошибка обновления: ${error.message}`
                                    )
                                  },
                                })
                              }
                              disabled={refreshGroupMutation.isPending}
                              className="h-8 w-8 hover:bg-blue-900 text-blue-400 hover:text-blue-300 transition-all duration-200"
                              title="Обновить группу"
                            >
                              <RefreshCw className="h-4 w-4" />
                            </Button>

                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleCopyLink(group?.screen_name || '')}
                              className="h-8 w-8 hover:bg-green-900 text-green-400 hover:text-green-300 transition-all duration-200"
                              title="Копировать ссылку"
                            >
                              {copiedGroup === group?.screen_name ? (
                                <Check className="h-4 w-4" />
                              ) : (
                                <Copy className="h-4 w-4" />
                              )}
                            </Button>

                            <Button
                              asChild
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 hover:bg-blue-900 text-blue-400 hover:text-blue-300 transition-all duration-200"
                              title="Открыть в VK"
                            >
                              <a
                                href={`https://vk.com/${group?.screen_name}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </Button>

                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() =>
                                updateGroupMutation.mutate({
                                  groupId: group?.id || 0,
                                  data: { is_active: !group?.is_active },
                                })
                              }
                              disabled={updateGroupMutation.isPending}
                              className="h-8 w-8 hover:bg-slate-600/50 text-blue-400 hover:text-blue-300 transition-all duration-200 rounded-md"
                              title={
                                group?.is_active ? 'Остановить' : 'Запустить'
                              }
                            >
                              {group?.is_active ? (
                                <Pause className="h-4 w-4" />
                              ) : (
                                <Play className="h-4 w-4" />
                              )}
                            </Button>

                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() =>
                                deleteGroupMutation.mutate(group?.id || 0)
                              }
                              disabled={deleteGroupMutation.isPending}
                              className="h-8 w-8 hover:bg-red-900 text-red-400 hover:text-red-300 transition-all duration-200"
                              title="Удалить группу"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Элемент для отслеживания скролла */}
              <div ref={observerRef} className="h-4" />

              {/* Индикатор загрузки */}
              {isFetchingNextPage && (
                <div className="p-3 text-center border-t border-slate-700">
                  <div className="flex items-center justify-center gap-2 text-slate-400">
                    <LoadingSpinner className="h-4 w-4" />
                    <span className="text-sm">Загрузка групп...</span>
                  </div>
                </div>
              )}

              {/* Сообщение о конце списка */}
              {!hasNextPage && groups.length > 0 && (
                <div className="p-3 text-center border-t border-slate-700">
                  <span className="text-sm text-slate-400">
                    Все группы загружены
                  </span>
                </div>
              )}

              {groups.length === 0 && !isFetching && (
                <div className="text-center py-12">
                  <div className="flex flex-col items-center justify-center space-y-3">
                    <div className="w-12 h-12 bg-slate-700 rounded-full flex items-center justify-center">
                      <Users className="h-6 w-6 text-slate-400" />
                    </div>
                    <p className="text-slate-400 font-medium text-sm">
                      {searchTerm
                        ? 'Группы не найдены'
                        : 'Нет добавленных групп'}
                    </p>
                    <p className="text-slate-500 text-xs">
                      {searchTerm
                        ? 'Попробуйте изменить параметры поиска'
                        : 'Добавьте первую группу для начала работы'}
                    </p>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
