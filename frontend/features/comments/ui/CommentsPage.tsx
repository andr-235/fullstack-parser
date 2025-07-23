'use client'

import React, { useState, useMemo, useEffect } from 'react'
import { useInfiniteComments, useMarkCommentAsViewed, useArchiveComment, useUnarchiveComment } from '@/entities/comment'
import { useGroups } from '@/entities/group'
import { useKeywords } from '@/entities/keyword'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { LoadingSpinner } from '@/shared/ui'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import {
  Search,
  ExternalLink,
  XCircle,
  MessageSquare,
  Users,
  Target,
  Filter,
  ChevronDown,
  ChevronUp,
  Eye,
  EyeOff,
  Archive,
  ArchiveRestore,
  CheckCircle,
  Edit,
} from 'lucide-react'
import { useDebounce } from '@/shared/hooks'
import Link from 'next/link'
import type { VKCommentResponse, KeywordResponse } from '@/types/api'

// Helper to highlight keywords in text
const HighlightedText = ({
  text,
  keywords,
}: {
  text: string
  keywords: string[]
}) => {
  if (!keywords || keywords.length === 0) {
    return (
      <div className="text-slate-200 text-sm whitespace-pre-wrap break-words">
        {text}
      </div>
    )
  }

  // Экранируем специальные символы в ключевых словах для безопасного использования в regex
  const escapedKeywords = keywords.map((keyword) =>
    keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  )

  // Создаем regex для поиска всех совпадений
  const regex = new RegExp(`(${escapedKeywords.join('|')})`, 'gi')
  const parts = text.split(regex)

  return (
    <div className="text-slate-200 text-sm whitespace-pre-wrap break-words">
      {parts.map((part, i) => {
        // Проверяем, является ли часть ключевым словом (без учета регистра)
        const isKeyword = keywords.some(
          (kw) => kw.toLowerCase() === part.toLowerCase()
        )

        return isKeyword ? (
          <Badge
            key={i}
            className="mx-1 bg-gradient-to-r from-red-500 to-orange-500 text-white border-0 text-xs font-bold shadow-lg hover:from-red-600 hover:to-orange-600 transition-all duration-200"
            title={`Найдено ключевое слово: ${part}`}
          >
            {part}
          </Badge>
        ) : (
          part
        )
      })}
    </div>
  )
}

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
        <CardTitle className="text-base font-semibold text-slate-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-blue-400" />
            {title}
          </div>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          )}
        </CardTitle>
      </CardHeader>
      {isExpanded && <CardContent className="pt-0">{children}</CardContent>}
    </Card>
  )
}

export default function CommentsPage() {
  const [textFilter, setTextFilter] = useState('')
  const [groupFilter, setGroupFilter] = useState<string>('all')
  const [keywordFilter, setKeywordFilter] = useState<string | undefined>(undefined)
  const [statusFilter, setStatusFilter] = useState<string>('new')
  const [specialAuthor, setSpecialAuthor] = useState<string | null>(null)
  const [authorFilter, setAuthorFilter] = useState<string>('all')

  // Локальное состояние для отслеживания загружающихся комментариев
  const [loadingComments, setLoadingComments] = useState<{
    [key: string]: boolean
  }>({})

  const debouncedText = useDebounce(textFilter, 500)

  // Мутации для управления статусом
  const markAsViewed = useMarkCommentAsViewed()
  const archiveComment = useArchiveComment()
  const unarchiveComment = useUnarchiveComment()

  const getStatusParams = (status: string) => {
    switch (status) {
      case 'new':
        return { is_viewed: false }
      case 'viewed':
        return { is_viewed: true }
      case 'archived':
        return { is_archived: true }
      default:
        return {}
    }
  }

  const getAuthorParams = () => {
    if (authorFilter === 'special' && specialAuthor) {
      // Преобразуем author_screen_name в author_id
      const match = specialAuthor.match(/^id(\d+)$/)
      const authorId = match ? parseInt(match[1]) : null

      return authorId ? { author_id: authorId } : {}
    }
    return {}
  }

  useEffect(() => {
    const statusParams = getStatusParams(statusFilter)
    const authorParams = getAuthorParams()
    console.log('=== FILTERS DEBUG ===')
    console.log('authorFilter:', authorFilter)
    console.log('specialAuthor:', specialAuthor)
    console.log('authorParams:', authorParams)
    console.log('statusParams:', statusParams)
    console.log('all filters:', {
      text: debouncedText,
      group_id: groupFilter && groupFilter !== 'all' ? Number(groupFilter) : undefined,
      keyword_id: keywordFilter ? Number(keywordFilter) : undefined,
      ...statusParams,
      ...authorParams,
    })
  }, [groupFilter, debouncedText, keywordFilter, statusFilter, authorFilter, specialAuthor])

  const statusParams = getStatusParams(statusFilter)
  const authorParams = getAuthorParams()

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
    refetch,
  } = useInfiniteComments({
    text: debouncedText,
    group_id: groupFilter && groupFilter !== 'all' ? Number(groupFilter) : undefined,
    keyword_id: keywordFilter ? Number(keywordFilter) : undefined,
    ...statusParams,
    ...authorParams,
  })

  // Принудительно обновляем при изменении фильтров
  useEffect(() => {
    refetch()
  }, [authorFilter, specialAuthor, refetch])

  const { data: groupsData } = useGroups()
  const { data: keywordsData } = useKeywords()
  const comments = useMemo(
    () => data?.pages.flatMap((page) => page.items) ?? [],
    [data]
  )

  const handleResetFilters = () => {
    setTextFilter('')
    setGroupFilter('all')
    setKeywordFilter(undefined)
    setStatusFilter('new')
    setAuthorFilter('all')
    setSpecialAuthor(null)
  }

  const handleAddSpecialAuthor = (authorScreenName: string) => {
    setSpecialAuthor(authorScreenName)
    // Автоматически переключаем фильтр на особые авторы
    setAuthorFilter('special')
  }

  const handleMarkAsViewed = async (commentId: number) => {
    const key = `view-${commentId}`
    setLoadingComments(prev => ({ ...prev, [key]: true }))
    try {
      // Сначала отмечаем как просмотренный, затем сразу архивируем
      await markAsViewed.mutateAsync(commentId)
      await archiveComment.mutateAsync(commentId)
    } catch (error) {
      // Ошибка уже обрабатывается в хуке
    } finally {
      setLoadingComments(prev => ({ ...prev, [key]: false }))
    }
  }

  const handleArchiveComment = async (commentId: number) => {
    const key = `archive-${commentId}`
    setLoadingComments(prev => ({ ...prev, [key]: true }))
    try {
      await archiveComment.mutateAsync(commentId)
    } catch (error) {
      // Ошибка уже обрабатывается в хуке
    } finally {
      setLoadingComments(prev => ({ ...prev, [key]: false }))
    }
  }

  const handleUnarchiveComment = async (commentId: number) => {
    const key = `unarchive-${commentId}`
    setLoadingComments(prev => ({ ...prev, [key]: true }))
    try {
      await unarchiveComment.mutateAsync(commentId)
    } catch (error) {
      // Ошибка уже обрабатывается в хуке
    } finally {
      setLoadingComments(prev => ({ ...prev, [key]: false }))
    }
  }

  // Функции для проверки состояния загрузки конкретного комментария
  const isMarkingAsViewed = (commentId: number) =>
    loadingComments[`view-${commentId}`] || false

  const isArchiving = (commentId: number) =>
    loadingComments[`archive-${commentId}`] || false

  const isUnarchiving = (commentId: number) =>
    loadingComments[`unarchive-${commentId}`] || false

  // Статистика
  const totalComments = 0 // Global stats are removed, so this will be 0
  const totalGroups = 0 // Global stats are removed, so this will be 0
  const totalKeywords = 0 // Global stats are removed, so this will be 0

  return (
    <div className="space-y-4">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-4 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <MessageSquare className="h-5 w-5" />
          </div>
          <h1 className="text-xl font-bold">Просмотр комментариев</h1>
        </div>
        <p className="text-slate-300 text-sm">
          Фильтрация и просмотр комментариев с ключевыми словами. По умолчанию показываются новые комментарии.
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
                  <MessageSquare className="h-4 w-4 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">
                    Комментариев
                  </p>
                  <p className="text-lg font-bold text-blue-400">
                    {totalComments}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-700 rounded-lg">
                  <Users className="h-4 w-4 text-green-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">Групп</p>
                  <p className="text-lg font-bold text-green-400">
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
                  <Target className="h-4 w-4 text-purple-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">
                    Ключевых слов
                  </p>
                  <p className="text-lg font-bold text-purple-400">
                    {totalKeywords}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </CollapsibleSection>

      {/* Фильтры */}
      <CollapsibleSection
        title="Фильтры комментариев"
        icon={Filter}
        defaultExpanded={false}
      >
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-3">
            <div className="md:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Поиск по тексту комментария..."
                value={textFilter}
                onChange={(e) => setTextFilter(e.target.value)}
                className="pl-10 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400 text-sm"
                aria-label="Поиск по тексту"
              />
            </div>
            <Select
              value={groupFilter}
              onValueChange={(val) => setGroupFilter(val)}
            >
              <SelectTrigger
                className="border-slate-600 bg-slate-700 text-slate-200 text-sm"
                aria-label="Группа"
              >
                <SelectValue placeholder="Все группы" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem
                  value="all"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Все группы
                </SelectItem>
                {groupsData?.items?.map((group) => (
                  <SelectItem
                    key={group.id}
                    value={String(group.id)}
                    className="text-slate-200 hover:bg-slate-700 text-sm"
                  >
                    {group.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={keywordFilter ? String(keywordFilter) : 'all'}
              onValueChange={(val) =>
                setKeywordFilter(val === 'all' ? undefined : val)
              }
            >
              <SelectTrigger
                className="border-slate-600 bg-slate-700 text-slate-200 text-sm"
                aria-label="Ключевое слово"
              >
                <SelectValue placeholder="Все ключевые слова" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem
                  value="all"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Все ключевые слова
                </SelectItem>
                {keywordsData?.items?.map((keyword) => (
                  <SelectItem
                    key={keyword.id}
                    value={String(keyword.id)}
                    className="text-slate-200 hover:bg-slate-700 text-sm"
                  >
                    {keyword.word}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select
              value={statusFilter}
              onValueChange={(val) => setStatusFilter(val)}
            >
              <SelectTrigger
                className="border-slate-600 bg-slate-700 text-slate-200 text-sm"
                aria-label="Статус комментария"
              >
                <SelectValue placeholder="Статус" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem
                  value="new"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Новые
                </SelectItem>
                <SelectItem
                  value="viewed"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Просмотренные
                </SelectItem>
                <SelectItem
                  value="archived"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Архивные
                </SelectItem>
                <SelectItem
                  value="all"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Все
                </SelectItem>
              </SelectContent>
            </Select>
            <Select
              value={authorFilter}
              onValueChange={(val) => {
                setAuthorFilter(val)
              }}
            >
              <SelectTrigger
                className="border-slate-600 bg-slate-700 text-slate-200 text-sm"
                aria-label="Фильтр по автору"
              >
                <SelectValue placeholder="Все авторы" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem
                  value="all"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                >
                  Все авторы
                </SelectItem>
                <SelectItem
                  value="special"
                  className="text-slate-200 hover:bg-slate-700 text-sm"
                  disabled={!specialAuthor}
                >
                  Особый автор: {specialAuthor || 'Не выбран'}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex justify-end">
            <Button
              variant="outline"
              onClick={handleResetFilters}
              className="border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-slate-200 text-sm"
            >
              <XCircle className="h-3 w-3 mr-2" />
              Сбросить к новым
            </Button>
          </div>
        </div>
      </CollapsibleSection>

      {/* Таблица комментариев */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardContent className="p-0">
          {isFetching && !isFetchingNextPage ? (
            <div
              className="flex justify-center items-center h-48"
              role="status"
            >
              <div className="flex flex-col items-center justify-center space-y-4">
                <LoadingSpinner className="h-6 w-6 text-blue-500" />
                <span className="text-slate-400 font-medium text-sm">
                  Загрузка комментариев...
                </span>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-16">
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="w-12 h-12 bg-red-900 rounded-full flex items-center justify-center">
                  <XCircle className="h-6 w-6 text-red-400" />
                </div>
                <p className="text-red-400 font-medium text-sm">
                  Ошибка загрузки
                </p>
                <p className="text-slate-400 text-xs">{error.message}</p>
              </div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="bg-gradient-to-r from-slate-700 to-slate-600 shadow-md hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600">
                  <TableHead className="text-slate-200 text-xs font-bold w-48">
                    Автор
                  </TableHead>
                  <TableHead className="text-slate-200 text-xs font-bold w-96">
                    Комментарий
                  </TableHead>
                  <TableHead className="text-slate-200 text-xs font-bold w-32">
                    Группа
                  </TableHead>
                  <TableHead className="text-slate-200 text-xs font-bold w-24">
                    Дата
                  </TableHead>
                  <TableHead className="text-slate-200 text-xs font-bold w-20 text-center">
                    Статус
                  </TableHead>
                  <TableHead className="text-slate-200 text-xs font-bold w-32 text-right">
                    Действия
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {comments.map((comment: VKCommentResponse, index: number) => (
                  <TableRow
                    key={comment.id}
                    className={`group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01] ${comment.is_viewed ? 'opacity-60' : ''
                      }`}
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Avatar className="w-6 h-6 border border-slate-600">
                          <AvatarImage src={comment.author_photo_url} />
                          <AvatarFallback className="bg-slate-700 text-slate-300 text-xs">
                            {comment.author_name?.[0] || '?'}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium text-slate-200 text-xs">
                            {comment.author_name}
                          </div>
                          <div className="text-xs text-slate-400">
                            @{comment.author_screen_name}
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="align-top">
                      <div className="max-w-lg w-full">
                        <HighlightedText
                          text={comment.text}
                          keywords={comment.matched_keywords || []}
                        />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {comment.group ? (
                          <>
                            <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">
                                {comment.group.name?.charAt(0)?.toUpperCase() ||
                                  'G'}
                              </span>
                            </div>
                            <span className="text-sm text-slate-300 text-xs">
                              {comment.group.name}
                            </span>
                          </>
                        ) : (
                          <>
                            <div className="w-5 h-5 bg-gradient-to-br from-slate-600 to-slate-700 rounded-full flex items-center justify-center">
                              <span className="text-slate-400 text-xs font-bold">
                                ?
                              </span>
                            </div>
                            <span className="text-sm text-slate-500 text-xs">
                              Не указана
                            </span>
                          </>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                        <span className="text-sm text-slate-400 text-xs">
                          {format(
                            new Date(comment.published_at),
                            'dd.MM.yyyy HH:mm',
                            { locale: ru }
                          )}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center gap-1">
                        {comment.is_viewed ? (
                          <Badge variant="secondary" className="text-xs bg-gray-900 text-gray-300">
                            <Archive className="h-3 w-3 mr-1" />
                            Архив
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs bg-yellow-900 text-yellow-300">
                            <EyeOff className="h-3 w-3 mr-1" />
                            Новый
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {comment.group?.vk_id && comment.post_vk_id ? (
                          <Button
                            asChild
                            variant="ghost"
                            size="icon"
                            className="hover:bg-blue-900 text-blue-400 hover:text-blue-300 transition-all duration-200 hover:scale-110 h-8 w-8"
                          >
                            <Link
                              href={`https://vk.com/wall-${comment.group.vk_id}_${comment.post_vk_id}?reply=${comment.vk_id}`}
                              target="_blank"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </Link>
                          </Button>
                        ) : null}

                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => comment.author_screen_name && handleAddSpecialAuthor(comment.author_screen_name)}
                          className="hover:bg-purple-900 text-purple-400 hover:text-purple-300 transition-all duration-200 hover:scale-110 h-8 w-8"
                          title="Добавить автора в особый статус"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>

                        {!comment.is_viewed && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleMarkAsViewed(comment.id)}
                            disabled={isMarkingAsViewed(comment.id)}
                            className="hover:bg-green-900 text-green-400 hover:text-green-300 transition-all duration-200 hover:scale-110 h-8 w-8"
                            title="Отметить как просмотренный и архивировать"
                          >
                            {isMarkingAsViewed(comment.id) ? (
                              <LoadingSpinner className="h-4 w-4" />
                            ) : (
                              <CheckCircle className="h-4 w-4" />
                            )}
                          </Button>
                        )}

                        {comment.is_viewed && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleUnarchiveComment(comment.id)}
                            disabled={isUnarchiving(comment.id)}
                            className="hover:bg-blue-900 text-blue-400 hover:text-blue-300 transition-all duration-200 hover:scale-110 h-8 w-8"
                            title="Разархивировать"
                          >
                            {isUnarchiving(comment.id) ? (
                              <LoadingSpinner className="h-4 w-4" />
                            ) : (
                              <ArchiveRestore className="h-4 w-4" />
                            )}
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {/* Пагинация */}
          {hasNextPage && (
            <div className="p-3 text-center border-t border-slate-700">
              <Button
                onClick={() => fetchNextPage()}
                disabled={isFetchingNextPage}
                className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:scale-105 text-sm"
              >
                {isFetchingNextPage ? (
                  <>
                    <LoadingSpinner className="h-3 w-3 mr-2" />
                    Загрузка...
                  </>
                ) : (
                  'Загрузить еще'
                )}
              </Button>
            </div>
          )}

          {comments.length === 0 && !isFetching && (
            <div className="text-center py-12">
              <div className="flex flex-col items-center justify-center space-y-3">
                <div className="w-12 h-12 bg-slate-700 rounded-full flex items-center justify-center">
                  <MessageSquare className="h-6 w-6 text-slate-400" />
                </div>
                <p className="text-slate-400 font-medium text-sm">
                  Комментарии не найдены
                </p>
                <p className="text-slate-500 text-xs">
                  Попробуйте изменить параметры фильтрации
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
