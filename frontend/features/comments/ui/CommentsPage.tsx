'use client'

import React, { useState, useMemo, useEffect } from 'react'
import { useInfiniteComments } from '@/hooks/use-comments'
import { useGroups } from '@/hooks/use-groups'
import { useKeywords } from '@/hooks/use-keywords'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { formatDistanceToNow, format } from 'date-fns'
import { ru } from 'date-fns/locale'
import { Search, ExternalLink, XCircle, MessageSquare, Users, Target, Filter, ChevronDown, ChevronUp } from 'lucide-react'
import useDebounce from '@/hooks/use-debounce'
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
    return <div className="text-slate-200 text-sm whitespace-pre-wrap break-words">{text}</div>
  }

  const regex = new RegExp(`(${keywords.join('|')})`, 'gi')
  const parts = text.split(regex)

  return (
    <div className="text-slate-200 text-sm whitespace-pre-wrap break-words">
      {parts.map((part, i) =>
        keywords.some((kw) => new RegExp(`^${kw}$`, 'i').test(part)) ? (
          <Badge key={i} className="mx-1 bg-gradient-to-r from-red-500 to-orange-500 text-white border-0 text-xs font-bold shadow-lg">
            {part}
          </Badge>
        ) : (
          part
        )
      )}
    </div>
  )
}

// Сворачиваемый блок
const CollapsibleSection = ({
  title,
  icon: Icon,
  children,
  defaultExpanded = false
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
      {isExpanded && (
        <CardContent className="pt-0">
          {children}
        </CardContent>
      )}
    </Card>
  )
}

export default function CommentsPage() {
  const [textFilter, setTextFilter] = useState('')
  const [groupFilter, setGroupFilter] = useState<string>('all')
  const [keywordFilter, setKeywordFilter] = useState<string | undefined>(
    undefined
  )
  const debouncedText = useDebounce(textFilter, 500)

  useEffect(() => {
    console.log('CommentsPage rendered')
    console.log('groupFilter:', groupFilter)
    console.log('useInfiniteComments params:', {
      text: debouncedText,
      group_id:
        groupFilter && groupFilter !== 'all' ? Number(groupFilter) : undefined,
      keyword_id: keywordFilter ? Number(keywordFilter) : undefined,
      limit: 20,
    })
  }, [groupFilter, debouncedText, keywordFilter])

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
  } = useInfiniteComments({
    text: debouncedText,
    group_id:
      groupFilter && groupFilter !== 'all' ? Number(groupFilter) : undefined,
    keyword_id: keywordFilter ? Number(keywordFilter) : undefined,
    limit: 20,
  })

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
  }

  // Статистика
  const totalComments = comments.length
  const totalGroups = groupsData?.items?.length || 0
  const totalKeywords = keywordsData?.items?.length || 0

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
          Фильтрация и просмотр всех найденных комментариев с ключевыми словами
        </p>
      </div>

      {/* Статистика */}
      <CollapsibleSection title="Статистика" icon={Target} defaultExpanded={false}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
            <CardContent className="p-3">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-700 rounded-lg">
                  <MessageSquare className="h-4 w-4 text-blue-400" />
                </div>
                <div>
                  <p className="text-xs font-medium text-slate-300">Комментариев</p>
                  <p className="text-lg font-bold text-blue-400">{totalComments}</p>
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
                  <p className="text-lg font-bold text-green-400">{totalGroups}</p>
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
                  <p className="text-xs font-medium text-slate-300">Ключевых слов</p>
                  <p className="text-lg font-bold text-purple-400">{totalKeywords}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </CollapsibleSection>

      {/* Фильтры */}
      <CollapsibleSection title="Фильтры комментариев" icon={Filter} defaultExpanded={false}>
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
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
              <SelectTrigger className="border-slate-600 bg-slate-700 text-slate-200 text-sm" aria-label="Группа">
                <SelectValue placeholder="Все группы" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="all" className="text-slate-200 hover:bg-slate-700 text-sm">Все группы</SelectItem>
                {groupsData?.items?.map((group) => (
                  <SelectItem key={group.id} value={String(group.id)} className="text-slate-200 hover:bg-slate-700 text-sm">
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
              <SelectTrigger className="border-slate-600 bg-slate-700 text-slate-200 text-sm" aria-label="Ключевое слово">
                <SelectValue placeholder="Все ключевые слова" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-600">
                <SelectItem value="all" className="text-slate-200 hover:bg-slate-700 text-sm">Все ключевые слова</SelectItem>
                {keywordsData?.items?.map((keyword) => (
                  <SelectItem key={keyword.id} value={String(keyword.id)} className="text-slate-200 hover:bg-slate-700 text-sm">
                    {keyword.word}
                  </SelectItem>
                ))}
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
              Сбросить фильтры
            </Button>
          </div>
        </div>
      </CollapsibleSection>

      {/* Таблица комментариев */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardContent className="p-0">
          {isFetching && !isFetchingNextPage ? (
            <div className="flex justify-center items-center h-48" role="status">
              <div className="flex flex-col items-center justify-center space-y-4">
                <LoadingSpinner className="h-6 w-6 text-blue-500" />
                <span className="text-slate-400 font-medium text-sm">Загрузка комментариев...</span>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-16">
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="w-12 h-12 bg-red-900 rounded-full flex items-center justify-center">
                  <XCircle className="h-6 w-6 text-red-400" />
                </div>
                <p className="text-red-400 font-medium text-sm">Ошибка загрузки</p>
                <p className="text-slate-400 text-xs">{error.message}</p>
              </div>
            </div>
          ) : (
            <table className="min-w-full table-fixed">
              <thead className="bg-gradient-to-r from-slate-700 to-slate-600 shadow-md">
                <tr>
                  <th className="px-3 py-2 text-left font-bold text-slate-200 text-xs w-48">Автор</th>
                  <th className="px-3 py-2 text-left font-bold text-slate-200 text-xs w-96">Комментарий</th>
                  <th className="px-3 py-2 text-left font-bold text-slate-200 text-xs w-32">Группа</th>
                  <th className="px-3 py-2 text-left font-bold text-slate-200 text-xs w-24">Дата</th>
                  <th className="px-3 py-2 text-right font-bold text-slate-200 text-xs w-16">Ссылка</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {comments.map((comment: VKCommentResponse, index: number) => (
                  <tr
                    key={comment.id}
                    className="group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01]"
                    style={{ animationDelay: `${index * 30}ms` }}
                  >
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        <Avatar className="w-6 h-6 border border-slate-600">
                          <AvatarImage src={comment.author_photo_url} />
                          <AvatarFallback className="bg-slate-700 text-slate-300 text-xs">
                            {comment.author_name?.[0] || '?'}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <div className="font-medium text-slate-200 text-xs">{comment.author_name}</div>
                          <div className="text-xs text-slate-400">@{comment.author_screen_name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-2 align-top">
                      <div className="max-w-lg w-full">
                        <HighlightedText
                          text={comment.text}
                          keywords={comment.matched_keywords || []}
                        />
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        {comment.group ? (
                          <>
                            <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">
                                {comment.group.name?.charAt(0)?.toUpperCase() || 'G'}
                              </span>
                            </div>
                            <span className="text-sm text-slate-300 text-xs">{comment.group.name}</span>
                          </>
                        ) : (
                          <>
                            <div className="w-5 h-5 bg-gradient-to-br from-slate-600 to-slate-700 rounded-full flex items-center justify-center">
                              <span className="text-slate-400 text-xs font-bold">?</span>
                            </div>
                            <span className="text-sm text-slate-500 text-xs">Не указана</span>
                          </>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></span>
                        <span className="text-sm text-slate-400 text-xs">
                          {format(new Date(comment.published_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                        </span>
                      </div>
                    </td>
                    <td className="px-3 py-2 text-right">
                      {comment.group?.vk_id && comment.post_vk_id ? (
                        <Button
                          asChild
                          variant="ghost"
                          size="icon"
                          className="hover:bg-blue-900 text-blue-400 hover:text-blue-300 transition-all duration-200 hover:scale-110 h-6 w-6"
                        >
                          <Link
                            href={`https://vk.com/wall-${comment.group.vk_id}_${comment.post_vk_id}?reply=${comment.vk_id}`}
                            target="_blank"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </Link>
                        </Button>
                      ) : (
                        <div className="text-xs text-slate-500 px-2 py-1">
                          Нет ссылки
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
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
                <p className="text-slate-400 font-medium text-sm">Комментарии не найдены</p>
                <p className="text-slate-500 text-xs">Попробуйте изменить параметры фильтрации</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
