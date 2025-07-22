'use client'

import React, { useState, useMemo, useEffect } from 'react'
import {
  useInfiniteGroups,
  useCreateGroup,
  useUpdateGroup,
  useDeleteGroup,
  useRefreshGroupInfo,
} from '@/features/groups/hooks/use-groups'
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
import {
  Plus,
  Play,
  Pause,
  Trash2,
  Search,
  Upload,
  Users,
  MessageSquare,
  Activity,
  Eye,
  Settings,
  Copy,
  ExternalLink,
  Check,
  Target,
  Filter,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { VKGroupResponse } from '@/types/api'
import UploadGroupsModal from './UploadGroupsModal'
import { toast } from 'react-hot-toast'
import useDebounce from '@/hooks/use-debounce'
import { useInfiniteScroll } from '@/hooks/use-infinite-scroll'

const AVATAR_PLACEHOLDER =
  'https://ui-avatars.com/api/?background=0D8ABC&color=fff&name='

// Сворачиваемый блок
const CollapsibleSection = ({
  title,
  icon: Icon,
  children,
  defaultExpanded = false,
}: {
  title: string
  icon: React.ElementType
  children: React.ReactNode
  defaultExpanded?: boolean
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <Card className="border-slate-700 bg-slate-800 shadow-lg">
      <CardHeader
        className="pb-3 cursor-pointer hover:bg-slate-750 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Icon className="h-4 w-4 text-slate-400" />
            <CardTitle className="text-sm font-semibold text-slate-200">
              {title}
            </CardTitle>
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          )}
        </div>
      </CardHeader>
      {isExpanded && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  )
}

// Компонент для заголовка с сортировкой
const SortableHeader = ({
  children,
  field,
  currentSort,
  currentOrder,
  onSort,
  className = '',
}: {
  children: React.ReactNode
  field: 'name' | 'comments' | 'members' | 'last_parsed'
  currentSort: string
  currentOrder: string
  onSort: (field: 'name' | 'comments' | 'members' | 'last_parsed') => void
  className?: string
}) => {
  const isActive = currentSort === field

  return (
    <th
      className={`px-4 py-3 text-left font-bold text-slate-200 cursor-pointer hover:bg-slate-600 transition-colors select-none ${className}`}
      onClick={() => onSort(field)}
    >
      <div className="flex items-center gap-2">
        {children}
        <div className="flex flex-col">
          {isActive ? (
            currentOrder === 'asc' ? (
              <ArrowUp className="h-3 w-3 text-blue-400" />
            ) : (
              <ArrowDown className="h-3 w-3 text-blue-400" />
            )
          ) : (
            <ArrowUpDown className="h-3 w-3 text-slate-400" />
          )}
        </div>
      </div>
    </th>
  )
}

export default function GroupsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeOnly, setActiveOnly] = useState(false)
  const [newGroupUrl, setNewGroupUrl] = useState('')
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
  } = useInfiniteGroups({
    active_only: activeOnly,
    search: debouncedSearch,
  })

  const createGroupMutation = useCreateGroup()
  const updateGroupMutation = useUpdateGroup()
  const deleteGroupMutation = useDeleteGroup()
  const refreshGroupMutation = useRefreshGroupInfo()

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
        onSuccess: () => {
          setNewGroupUrl('')
          toast.success('Группа успешно добавлена! 🎉')
        },
        onError: (error: any) => {
          console.error('Ошибка создания группы:', error)
          console.error('Error status:', error?.status)
          console.error('Error response status:', error?.response?.status)
          console.error('Error response data:', error?.response?.data)
          console.error('Error message:', error?.message)
          console.error('Error name:', error?.name)
          console.error('Full error object:', JSON.stringify(error, null, 2))

          let errorMessage = 'Ошибка при создании группы'

          // Проверяем различные форматы ошибок
          if (error?.status === 409 || error?.response?.status === 409) {
            // Группа уже существует
            errorMessage =
              error?.response?.data?.detail ||
              error?.message ||
              'Группа уже существует в системе'
            toast.error(errorMessage)
          } else if (error?.response?.data?.detail) {
            errorMessage = error.response.data.detail
            toast.error(errorMessage)
          } else if (error?.data?.detail) {
            // Альтернативный формат ошибки
            errorMessage = error.data.detail
            toast.error(errorMessage)
          } else if (error?.message) {
            errorMessage = error.message
            toast.error(errorMessage)
          } else if (error?.error) {
            // Еще один возможный формат
            errorMessage = error.error
            toast.error(errorMessage)
          } else {
            toast.error(errorMessage)
          }
        },
      }
    )
  }

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
  const activeGroups = groups.filter((group) => group.is_active).length
  const inactiveGroups = totalGroups - activeGroups

  return (
    <div className="space-y-4">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-4 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <Users className="h-5 w-5" />
          </div>
          <h1 className="text-xl font-bold">Управление группами</h1>
        </div>
        <p className="text-slate-300 text-sm">
          Добавление, настройка и мониторинг VK групп для парсинга
        </p>
      </div>

      {/* Статистика */}
      <CollapsibleSection
        title="Статистика"
        icon={Target}
        defaultExpanded={false}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-700 rounded-lg">
                  <Users className="h-4 w-4 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">
                    Всего групп
                  </p>
                  <p className="text-lg font-bold text-blue-400">
                    {totalGroups}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-700 rounded-lg">
                  <Activity className="h-4 w-4 text-green-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">Активных</p>
                  <p className="text-lg font-bold text-green-400">
                    {activeGroups}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-700 rounded-lg">
                  <Pause className="h-4 w-4 text-orange-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">
                    Неактивных
                  </p>
                  <p className="text-lg font-bold text-orange-400">
                    {inactiveGroups}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </CollapsibleSection>

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
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Поиск по названию или screen_name..."
                className="pl-10 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={activeOnly}
                  onChange={() => setActiveOnly((v) => !v)}
                  className="rounded border-slate-600 bg-slate-700 text-blue-500 focus:ring-blue-500"
                />
                <span>Только активные</span>
              </label>

              <UploadGroupsModal onSuccess={() => {}} />
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
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardContent className="p-0">
          {isFetching && !data ? (
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
              <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden shadow-lg">
                <div className="overflow-x-auto">
                  <table className="min-w-full relative">
                    <thead className="sticky top-0 z-10 bg-gradient-to-r from-slate-700 to-slate-600 shadow-md">
                      <tr>
                        <th className="px-4 py-3 text-left font-bold text-slate-200 w-20">
                          ID
                        </th>
                        <SortableHeader
                          field="name"
                          currentSort={sortBy}
                          currentOrder={sortOrder}
                          onSort={handleSort}
                          className="w-80"
                        >
                          Группа
                        </SortableHeader>
                        <th className="px-4 py-3 text-left font-bold text-slate-200 w-24">
                          Статус
                        </th>
                        <SortableHeader
                          field="comments"
                          currentSort={sortBy}
                          currentOrder={sortOrder}
                          onSort={handleSort}
                          className="w-32"
                        >
                          Комментарии
                        </SortableHeader>
                        <SortableHeader
                          field="members"
                          currentSort={sortBy}
                          currentOrder={sortOrder}
                          onSort={handleSort}
                          className="w-32"
                        >
                          Участники
                        </SortableHeader>
                        <SortableHeader
                          field="last_parsed"
                          currentSort={sortBy}
                          currentOrder={sortOrder}
                          onSort={handleSort}
                          className="w-40"
                        >
                          Последний парсинг
                        </SortableHeader>
                        <th className="px-4 py-3 text-right font-bold text-slate-200 w-24">
                          Действия
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                      {groups.map((group, index) => (
                        <tr
                          key={group.id}
                          className={`group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01] ${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'}`}
                          style={{
                            animationDelay: `${index * 50}ms`,
                            animationFillMode: 'both',
                          }}
                        >
                          <td className="px-4 py-3 font-mono text-blue-400 font-semibold w-20">
                            {group.vk_id}
                          </td>
                          <td className="px-4 py-3 w-80">
                            <div className="flex items-center gap-2">
                              <div className="relative flex-shrink-0">
                                <img
                                  src={
                                    group.photo_url ||
                                    `${AVATAR_PLACEHOLDER}${encodeURIComponent(group.name)}`
                                  }
                                  alt={group.name}
                                  className="w-8 h-8 rounded-full border-2 border-slate-600 shadow-sm object-cover bg-slate-700 transition-transform duration-200 hover:scale-110"
                                  loading="lazy"
                                />
                                {group.is_active && (
                                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-slate-800 animate-pulse"></div>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-1">
                                  <h3 className="font-semibold text-slate-200 truncate text-sm">
                                    {group.name}
                                  </h3>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => {
                                      refreshGroupMutation.mutate(group.id, {
                                        onSuccess: () => {
                                          toast.success(
                                            'Информация о группе обновлена! 🔄'
                                          )
                                        },
                                        onError: (error: any) => {
                                          console.error(
                                            'Ошибка обновления группы:',
                                            error
                                          )
                                          toast.error(
                                            'Ошибка обновления информации о группе'
                                          )
                                        },
                                      })
                                    }}
                                    disabled={refreshGroupMutation.isPending}
                                    className="h-4 w-4 hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-all duration-200"
                                    title="Обновить информацию о группе из VK"
                                  >
                                    <RefreshCw className="h-3 w-3" />
                                  </Button>
                                </div>
                                <div className="flex items-center gap-1 mt-1">
                                  <span className="text-xs text-slate-400 truncate">
                                    @{group.screen_name}
                                  </span>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() =>
                                      handleCopyLink(group.screen_name)
                                    }
                                    className="h-4 w-4 hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-all duration-200"
                                  >
                                    {copiedGroup === group.screen_name ? (
                                      <Check className="h-2 w-2" />
                                    ) : (
                                      <Copy className="h-2 w-2" />
                                    )}
                                  </Button>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    asChild
                                    className="h-4 w-4 hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-all duration-200"
                                  >
                                    <a
                                      href={`https://vk.com/${group.screen_name}`}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                    >
                                      <ExternalLink className="h-2 w-2" />
                                    </a>
                                  </Button>
                                </div>
                              </div>
                            </div>
                          </td>
                          <td className="px-4 py-3 w-24">
                            <div className="flex items-center gap-2">
                              <Badge
                                variant={
                                  group.is_active ? 'default' : 'secondary'
                                }
                                className={`${
                                  group.is_active
                                    ? 'bg-green-600 hover:bg-green-700'
                                    : 'bg-slate-600 hover:bg-slate-700'
                                } text-white`}
                              >
                                {group.is_active ? 'Активна' : 'Неактивна'}
                              </Badge>
                              {/* Убираем проверку auto_monitoring_enabled, так как это поле не существует в VKGroupResponse */}
                              {/* {group.auto_monitoring_enabled && (
                                <Badge
                                  variant="outline"
                                  className="text-xs border-blue-500 text-blue-400"
                                >
                                  Мониторинг
                                </Badge>
                              )} */}
                            </div>
                          </td>
                          <td className="px-4 py-3 w-32">
                            <div className="flex items-center gap-2">
                              <MessageSquare className="h-4 w-4 text-blue-400" />
                              <span className="font-semibold text-slate-200">
                                {group.total_comments_found?.toLocaleString() ||
                                  '0'}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3 w-32">
                            <div className="flex items-center gap-2">
                              <Users className="h-4 w-4 text-green-400" />
                              <span className="font-semibold text-slate-200">
                                {group.members_count?.toLocaleString() || 'N/A'}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3 w-40">
                            <div className="text-sm text-slate-400">
                              {group.last_parsed_at ? (
                                <div className="flex items-center gap-2">
                                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                                  <span>
                                    {formatDistanceToNow(
                                      new Date(group.last_parsed_at),
                                      { addSuffix: true, locale: ru }
                                    )}
                                  </span>
                                </div>
                              ) : (
                                <span className="text-slate-500">Никогда</span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-right w-24">
                            <div className="flex items-center justify-end gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() =>
                                  updateGroupMutation.mutate({
                                    groupId: group.id,
                                    data: { is_active: !group.is_active },
                                  })
                                }
                                disabled={updateGroupMutation.isPending}
                                className="h-8 w-8 hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-all duration-200"
                                title={
                                  group.is_active ? 'Остановить' : 'Запустить'
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
                                className="h-8 w-8 hover:bg-slate-700 text-slate-400 hover:text-green-400 transition-all duration-200"
                                title="Настройки"
                              >
                                <Settings className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() =>
                                  deleteGroupMutation.mutate(group.id)
                                }
                                disabled={deleteGroupMutation.isPending}
                                className="h-8 w-8 hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-all duration-200"
                                title="Удалить"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
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
