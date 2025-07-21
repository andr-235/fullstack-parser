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
} from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import type { VKGroupResponse } from '@/types/api'
import UploadGroupsModal from './UploadGroupsModal'
import { toast } from 'react-hot-toast'

const AVATAR_PLACEHOLDER =
  'https://ui-avatars.com/api/?background=0D8ABC&color=fff&name='

export default function GroupsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeOnly, setActiveOnly] = useState(false)
  const [newGroupUrl, setNewGroupUrl] = useState('')
  const [copiedGroup, setCopiedGroup] = useState<string | null>(null)
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
          let errorMessage = 'Ошибка при создании группы'

          if (error?.response?.data?.detail) {
            errorMessage = error.response.data.detail
          } else if (error?.message) {
            errorMessage = error.message
          }

          toast.error(errorMessage)
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

  let filteredGroups = groupsData?.items || []
  if (searchTerm) {
    filteredGroups = filteredGroups.filter(
      (group) =>
        group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        group.screen_name.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }
  if (activeOnly) {
    filteredGroups = filteredGroups.filter((group) => group.is_active)
  }

  const renderContent = () => {
    if (isLoading && !groupsData) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
          <div className="relative">
            <LoadingSpinner className="h-8 w-8 text-blue-500" />
            <div className="absolute inset-0 rounded-full border-2 border-blue-200 animate-ping"></div>
          </div>
          <span className="text-slate-600 font-medium">Загрузка групп...</span>
        </div>
      )
    }

    if (error) {
      return (
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
      )
    }

    if (filteredGroups.length === 0) {
      return (
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 mb-4">
            <Users className="h-8 w-8 text-slate-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-900 mb-2">
            {searchTerm ? 'Группы не найдены' : 'Нет добавленных групп'}
          </h3>
          <p className="text-slate-600">
            {searchTerm
              ? 'Попробуйте изменить параметры поиска'
              : 'Добавьте первую группу для начала работы'}
          </p>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        <div className="bg-gradient-to-r from-slate-800 to-slate-700 rounded-lg p-4 border border-slate-600">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Activity className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-200">
                  Активные группы
                </p>
                <p className="text-xs text-slate-400">
                  {filteredGroups.filter((g) => g.is_active).length} из{' '}
                  {filteredGroups.length} групп
                </p>
              </div>
            </div>
            <Badge
              variant="outline"
              className="bg-slate-700 border-slate-600 text-slate-200"
            >
              {filteredGroups.filter((g) => g.is_active).length} активных
            </Badge>
          </div>
        </div>

        <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden shadow-lg">
          <div className="overflow-x-auto max-h-[420px] scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
            <table className="min-w-full relative">
              <thead className="sticky top-0 z-10 bg-gradient-to-r from-slate-700 to-slate-600 shadow-md">
                <tr>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    ID
                  </th>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Группа
                  </th>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Статус
                  </th>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Последний парсинг
                  </th>
                  <th className="px-4 py-3 text-right font-bold text-slate-200">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {filteredGroups.map((group, index) => (
                  <tr
                    key={group.id}
                    className={`group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01] ${index % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'}`}
                    style={{
                      animationDelay: `${index * 50}ms`,
                      animationFillMode: 'both',
                    }}
                  >
                    <td className="px-4 py-3 font-mono text-blue-400 font-semibold">
                      {group.vk_id}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <img
                            src={
                              group.photo_url ||
                              `${AVATAR_PLACEHOLDER}${encodeURIComponent(group.name)}`
                            }
                            alt={group.name}
                            className="w-10 h-10 rounded-full border-2 border-slate-600 shadow-sm object-cover bg-slate-700 transition-transform duration-200 hover:scale-110"
                            loading="lazy"
                          />
                          {group.is_active && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-slate-800 animate-pulse"></div>
                          )}
                        </div>
                        <div>
                          <div className="font-bold text-slate-200 text-base leading-tight flex items-center gap-1">
                            {group.name}
                            {group.is_closed && (
                              <span className="ml-1 px-2 py-0.5 rounded bg-yellow-900 text-yellow-300 text-xs font-semibold animate-bounce">
                                Приват
                              </span>
                            )}
                          </div>
                          <div className="text-xs text-blue-400 font-mono">
                            @{group.screen_name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold shadow-sm transition-all duration-200 ${group.is_active ? 'bg-gradient-to-r from-green-900 to-emerald-900 text-green-300 hover:from-green-800 hover:to-emerald-800' : 'bg-gradient-to-r from-slate-700 to-gray-700 text-slate-400 hover:from-slate-600 hover:to-gray-600'}`}
                      >
                        <span
                          className={`w-2 h-2 rounded-full ${group.is_active ? 'bg-green-400 animate-pulse' : 'bg-slate-500'}`}
                        ></span>
                        {group.is_active ? 'Активна' : 'На паузе'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {group.last_parsed_at ? (
                        <span className="flex items-center gap-2 text-blue-400 font-medium">
                          <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                          {formatDistanceToNow(new Date(group.last_parsed_at), {
                            addSuffix: true,
                            locale: ru,
                          })}
                        </span>
                      ) : (
                        <span className="flex items-center gap-2 text-slate-500 font-medium">
                          <span className="w-2 h-2 bg-slate-500 rounded-full"></span>
                          Никогда
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label="Открыть в VK"
                          className="hover:bg-slate-700 text-slate-300 hover:text-blue-400 transition-all duration-200 hover:scale-110 group"
                          onClick={() =>
                            window.open(
                              `https://vk.com/${group.screen_name}`,
                              '_blank'
                            )
                          }
                        >
                          <ExternalLink className="h-4 w-4 group-hover:rotate-12 transition-transform" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label="Копировать ссылку"
                          className={`transition-all duration-200 hover:scale-110 ${copiedGroup === group.screen_name ? 'bg-green-900 text-green-400' : 'hover:bg-slate-700 text-slate-300 hover:text-blue-400'}`}
                          onClick={() => handleCopyLink(group.screen_name)}
                        >
                          {copiedGroup === group.screen_name ? (
                            <Check className="h-4 w-4 animate-bounce" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={
                            group.is_active ? 'Приостановить' : 'Возобновить'
                          }
                          disabled={updateGroupMutation.isPending}
                          className="hover:bg-slate-700 text-slate-300 hover:text-slate-200 transition-all duration-200 hover:scale-110"
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
                          aria-label="удалить"
                          className="hover:bg-red-900 text-red-400 hover:text-red-300 transition-all duration-200 hover:scale-110"
                          disabled={deleteGroupMutation.isPending}
                          data-testid="delete-group"
                          onClick={() => {
                            deleteGroupMutation.mutate(group.id)
                          }}
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
      </div>
    )
  }

  // Статистика
  const totalGroups = groupsData?.items?.length || 0
  const activeGroups = groupsData?.items?.filter((g) => g.is_active).length || 0
  const inactiveGroups =
    groupsData?.items?.filter((g) => !g.is_active).length || 0
  const totalComments =
    groupsData?.items?.reduce(
      (sum, g) => sum + (g.total_comments_found || 0),
      0
    ) || 0
  const formattedTotalComments = new Intl.NumberFormat('ru-RU').format(
    totalComments
  )

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <Users className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold">Управление группами ВКонтакте</h1>
        </div>
        <p className="text-slate-300">
          Добавляйте, настраивайте и управляйте группами для парсинга
          комментариев
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Users className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">
                  Всего групп
                </p>
                <p className="text-2xl font-bold text-blue-400">
                  {totalGroups}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Activity className="h-5 w-5 text-green-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Активных</p>
                <p className="text-2xl font-bold text-green-400">
                  {activeGroups}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Pause className="h-5 w-5 text-orange-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Неактивных</p>
                <p className="text-2xl font-bold text-orange-400">
                  {inactiveGroups}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <MessageSquare className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">
                  Комментариев
                </p>
                <p className="text-2xl font-bold text-purple-400">
                  {formattedTotalComments}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Управление */}
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
        <CardContent className="p-0">{renderContent()}</CardContent>
      </Card>
    </div>
  )
}
