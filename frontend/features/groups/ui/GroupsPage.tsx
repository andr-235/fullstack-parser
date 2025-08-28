'use client'

import React, { useState, useMemo } from 'react'
import {
  useInfiniteGroups,
  useUpdateGroup,
  useDeleteGroup,
  useRefreshGroupInfo,
} from '@/features/groups/hooks'
import {
  PageHeader,
  StatsGrid,
  StatsCard,
  DataTable,
  LoadingState,
  EmptyState,
  ErrorState,
  SearchInput,
  FilterPanel,
  useSearch,
  useFilters,
  PageContainer,
} from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Input } from '@/shared/ui'
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
  Plus,
  Activity,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { VKGroupResponse } from '@/shared/types'
import { toast } from 'react-hot-toast'
import { useDebounce, useInfiniteScroll } from '@/shared/hooks'
import { useCreateGroup } from '@/features/groups/hooks'
import { UploadGroupsModal } from './components/UploadGroupsModal'

const AVATAR_PLACEHOLDER =
  'https://ui-avatars.com/api/?background=0D8ABC&color=fff&name='

export default function GroupsPage() {
  const [copiedGroup, setCopiedGroup] = useState<string | null>(null)
  const [newGroupUrl, setNewGroupUrl] = useState('')
  const [sortBy, setSortBy] = useState<
    'comments' | 'members' | 'name' | 'last_parsed'
  >('comments')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Фильтры
  const { filters, updateFilter } = useFilters({
    search: '',
    active_only: false,
  })

  const debouncedSearch = useDebounce(filters.search, 500)
  const createGroupMutation = useCreateGroup()

  // Конфигурация колонок для DataTable
  const columns = [
    {
      key: 'vk_id' as keyof VKGroupResponse,
      title: 'ID',
      width: '80px',
      render: (value: number) => (
        <span className="font-mono text-blue-400 font-semibold whitespace-nowrap">
          {value}
        </span>
      ),
    },
    {
      key: 'name' as keyof VKGroupResponse,
      title: 'Группа',
      sortable: true,
      width: '320px',
      render: (value: string, record: VKGroupResponse) => (
        <div className="flex items-center gap-2">
          <div className="relative flex-shrink-0">
            <img
              src={record.photo_url || `${AVATAR_PLACEHOLDER}${encodeURIComponent(record.name)}`}
              alt={record.name}
              className="w-6 h-6 rounded-full border border-slate-600 shadow-sm object-cover bg-slate-700 transition-transform duration-200 hover:scale-110"
              loading="lazy"
            />
            {record.is_active && (
              <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full border border-slate-800 animate-pulse"></div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <div>
              <h3 className="font-semibold text-slate-200 truncate text-sm">
                {record.name}
              </h3>
              <div className="text-xs text-slate-400 truncate mt-0.5">
                @{record.screen_name}
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      key: 'is_active' as keyof VKGroupResponse,
      title: 'Статус',
      render: (value: boolean) => (
        <Badge variant={value ? 'default' : 'secondary'} className={value ? 'bg-green-600 hover:bg-green-700' : 'bg-slate-600 hover:bg-slate-700'}>
          {value ? 'Активна' : 'Неактивна'}
        </Badge>
      ),
    },
    {
      key: 'total_comments_found' as keyof VKGroupResponse,
      title: 'Комментарии',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-blue-400" />
          <span className="font-semibold text-slate-200">
            {value?.toLocaleString() || '0'}
          </span>
        </div>
      ),
    },
    {
      key: 'members_count' as keyof VKGroupResponse,
      title: 'Участники',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-green-400" />
          <span className="font-semibold text-slate-200">
            {value?.toLocaleString() || 'N/A'}
          </span>
        </div>
      ),
    },
    {
      key: 'last_parsed_at' as keyof VKGroupResponse,
      title: 'Последний парсинг',
      sortable: true,
      render: (value: string) => (
        <div className="text-sm text-slate-400">
          {value ? (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
              <span>
                {(() => {
                  try {
                    const date = new Date(value)
                    return isNaN(date.getTime())
                      ? 'Неверная дата'
                      : formatDistanceToNow(date, { addSuffix: true, locale: ru })
                  } catch {
                    return 'Неверная дата'
                  }
                })()}
              </span>
            </div>
          ) : (
            <span className="text-slate-500">Никогда</span>
          )}
        </div>
      ),
    },
    {
      key: 'actions' as keyof VKGroupResponse,
      title: 'Действия',
      render: (value: any, record: VKGroupResponse) => (
        <div className="flex items-center justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              refreshGroupMutation.mutate(record.id, {
                onSuccess: () => {
                  toast.success('Информация о группе обновлена! 🔄')
                },
                onError: (error: any) => {
                  console.error('Ошибка обновления группы:', error)
                  toast.error('Ошибка обновления информации о группе')
                },
              })
            }}
            disabled={refreshGroupMutation.isPending}
            className="h-7 w-7 hover:bg-slate-600/50 text-blue-400 hover:text-blue-300 transition-all duration-200 rounded-md"
            title="Обновить информацию о группе из VK"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${refreshGroupMutation.isPending ? 'animate-spin' : ''}`} />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => handleCopyLink(record.screen_name)}
            className="h-7 w-7 hover:bg-slate-600/50 text-green-400 hover:text-green-300 transition-all duration-200 rounded-md"
            title="Копировать ссылку"
          >
            {copiedGroup === record.screen_name ? (
              <Check className="h-3.5 w-3.5" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            asChild
            className="h-7 w-7 hover:bg-slate-600/50 text-purple-400 hover:text-purple-300 transition-all duration-200 rounded-md"
            title="Открыть в VK"
          >
            <a
              href={`https://vk.com/${record.screen_name}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() =>
              updateGroupMutation.mutate({
                groupId: record.id,
                data: { is_active: !record.is_active },
              })
            }
            disabled={updateGroupMutation.isPending}
            className="h-8 w-8 hover:bg-slate-600/50 text-blue-400 hover:text-blue-300 transition-all duration-200 rounded-md"
            title={record.is_active ? 'Остановить' : 'Запустить'}
          >
            {record.is_active ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 hover:bg-slate-600/50 text-yellow-400 hover:text-yellow-300 transition-all duration-200 rounded-md"
            title="Настройки"
          >
            <Settings className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() =>
              deleteGroupMutation.mutate(record.id)
            }
            disabled={deleteGroupMutation.isPending}
            className="h-8 w-8 hover:bg-slate-600/50 text-red-400 hover:text-red-300 transition-all duration-200 rounded-md"
            title="Удалить"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ),
    },
  ]

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteGroups({
    active_only: filters.active_only,
    search: debouncedSearch,
  })

  const updateGroupMutation = useUpdateGroup()
  const deleteGroupMutation = useDeleteGroup()
  const refreshGroupMutation = useRefreshGroupInfo()

  const handleAddGroup = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newGroupUrl.trim()) return

    createGroupMutation.mutate(
      {
        vk_id_or_screen_name: newGroupUrl,
        is_active: true,
        max_posts_to_check: 100,
      },
      {
        onSuccess: (data) => {
          setNewGroupUrl('')
          toast.success('Группа успешно добавлена! 🎉')
        },
        onError: (error: any) => {
          let errorMessage = 'Ошибка при создании группы'

          if (error?.response?.status === 409) {
            errorMessage = error?.response?.data?.detail || 'Группа уже существует в системе'
          } else if (error?.response?.data?.detail) {
            errorMessage = error.response.data.detail
          } else if (error?.message) {
            errorMessage = error.message
          }

          toast.error(errorMessage)
        },
      }
    )
  }

  const groups = useMemo(() => {
    const allGroups = data?.pages.flatMap((page) => page.items) ?? []

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
          aValue = a.last_parsed_at ? (() => {
            const date = new Date(a.last_parsed_at)
            return isNaN(date.getTime()) ? 0 : date.getTime()
          })() : 0
          bValue = b.last_parsed_at ? (() => {
            const date = new Date(b.last_parsed_at)
            return isNaN(date.getTime()) ? 0 : date.getTime()
          })() : 0
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
      setTimeout(() => setCopiedGroup(null), 2000)
    } catch (err) {
      toast.error('Не удалось скопировать ссылку')
    }
  }

  // Статистика
  const totalGroups = data?.pages[0]?.total || 0
  const activeGroups = groups.filter((group) => group.is_active).length
  const inactiveGroups = totalGroups - activeGroups

  return (
    <PageContainer background="gradient">
      {/* Заголовок */}
      <PageHeader
        title="Управление группами"
        description="Добавление, настройка и мониторинг VK групп для парсинга"
        icon={Users}
      />

      {/* Статистика */}
      <StatsGrid
        stats={[
          {
            title: "Всего групп",
            value: totalGroups,
            icon: Users,
            color: "blue"
          },
          {
            title: "Активных",
            value: activeGroups,
            icon: Activity,
            color: "green"
          },
          {
            title: "Неактивных",
            value: inactiveGroups,
            icon: Pause,
            color: "orange"
          }
        ]}
      />

      {/* Управление группами */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold text-slate-200">
            Управление группами
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Поиск и фильтры */}
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <SearchInput
                value={filters.search}
                onChange={(value) => updateFilter('search', value)}
                placeholder="Поиск по названию или screen_name..."
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={filters.active_only}
                  onChange={(e) => updateFilter('active_only', e.target.checked)}
                  className="rounded border-slate-600 bg-slate-700 text-blue-500 focus:ring-blue-500"
                />
                <span>Только активные</span>
              </label>

              <UploadGroupsModal onSuccess={() => { }} />
            </div>
          </div>

          {/* Добавление новой группы */}
          <form onSubmit={handleAddGroup} className="flex gap-2">
            <Input
              placeholder="https://vk.com/example или example"
              value={newGroupUrl}
              onChange={(e) => setNewGroupUrl(e.target.value)}
              disabled={createGroupMutation.isPending}
              className="flex-1 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
            />
            <Button
              type="submit"
              disabled={createGroupMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 transition-all duration-200 hover:scale-105"
            >
              {createGroupMutation.isPending ? (
                <LoadingSpinner className="h-4 w-4" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              <span className="ml-2">Добавить</span>
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Таблица групп */}
      {error ? (
        <ErrorState
          title="Ошибка загрузки"
          message="Не удалось загрузить список групп"
          fullHeight={false}
        />
      ) : (
        <DataTable
          data={groups}
          columns={columns}
          loading={isLoading}
          emptyText={filters.search ? 'Группы не найдены' : 'Нет добавленных групп'}
          sortConfig={{
            key: sortBy as keyof VKGroupResponse,
            direction: sortOrder,
            onSort: (key, direction) => {
              setSortBy(key as typeof sortBy)
              setSortOrder(direction)
            },
          }}
        />
      )}

      {/* Элемент для отслеживания скролла */}
      {!error && !isLoading && hasNextPage && (
        <div ref={observerRef} className="h-4" />
      )}

      {/* Индикатор загрузки */}
      {!error && !isLoading && isFetchingNextPage && (
        <div className="flex items-center justify-center p-3 text-slate-400">
          <LoadingSpinner className="h-4 w-4 mr-2" />
          <span className="text-sm">Загрузка групп...</span>
        </div>
      )}

      {/* Сообщение о конце списка */}
      {!error && !isLoading && !hasNextPage && groups.length > 0 && (
        <div className="text-center p-3 text-slate-400">
          <span className="text-sm">Все группы загружены</span>
        </div>
      )}
    </PageContainer>
  )
}