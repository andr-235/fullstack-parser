'use client'

import React, { useState, useMemo } from 'react'
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
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'
import { Search, ExternalLink, XCircle } from 'lucide-react'
import useDebounce from '@/hooks/use-debounce'
import Link from 'next/link'
import type { VKCommentResponse, KeywordResponse } from '@/types/api'

// Helper to highlight keywords in text
const HighlightedText = ({
  text,
  keywords,
}: {
  text: string
  keywords: KeywordResponse[]
}) => {
  if (!keywords || keywords.length === 0) {
    return <span>{text}</span>
  }

  const keywordNames = keywords.map((k) => k.word)
  const regex = new RegExp(`(${keywordNames.join('|')})`, 'gi')
  const parts = text.split(regex)

  return (
    <span>
      {parts.map((part, i) =>
        keywordNames.some((kw) => new RegExp(`^${kw}$`, 'i').test(part)) ? (
          <Badge key={i} variant="success" className="mx-1">
            {part}
          </Badge>
        ) : (
          part
        )
      )}
    </span>
  )
}

export default function CommentsPage() {
  const [textFilter, setTextFilter] = useState('')
  const [groupFilter, setGroupFilter] = useState<string | undefined>(undefined)
  const [keywordFilter, setKeywordFilter] = useState<string | undefined>(
    undefined
  )
  const debouncedText = useDebounce(textFilter, 500)

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
  } = useInfiniteComments({
    text: debouncedText,
    group_id: groupFilter ? Number(groupFilter) : undefined,
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
    setGroupFilter(undefined)
    setKeywordFilter(undefined)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Лента комментариев</CardTitle>
        <CardDescription>
          Просмотр и фильтрация всех найденных комментариев.
        </CardDescription>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4">
          <Input
            placeholder="Поиск по тексту..."
            value={textFilter}
            onChange={(e) => setTextFilter(e.target.value)}
            className="md:col-span-2"
          />
          <Select value={groupFilter} onValueChange={setGroupFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Все группы" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="undefined">Все группы</SelectItem>
              {groupsData?.items?.map((group) => (
                <SelectItem key={group.id} value={String(group.id)}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleResetFilters}
              className="w-full"
            >
              <XCircle className="h-4 w-4 mr-2" />
              Сбросить
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isFetching && !isFetchingNextPage ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="text-center text-red-500 py-10">
            <p>Ошибка при загрузке комментариев.</p>
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Автор</TableHead>
                  <TableHead>Комментарий</TableHead>
                  <TableHead>Группа</TableHead>
                  <TableHead>Дата</TableHead>
                  <TableHead className="text-right">Ссылка</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {comments.map((comment: VKCommentResponse) => (
                  <TableRow key={comment.id}>
                    <TableCell className="flex items-center gap-2">
                      <Avatar>
                        <AvatarImage src={comment.author_photo_url} />
                        <AvatarFallback>
                          {comment.author_name?.[0] || '?'}
                        </AvatarFallback>
                      </Avatar>
                      <span>{comment.author_name}</span>
                    </TableCell>
                    <TableCell>
                      <HighlightedText
                        text={comment.text}
                        keywords={comment.matched_keywords || []}
                      />
                    </TableCell>
                    <TableCell>{comment.group?.name || 'N/A'}</TableCell>
                    <TableCell>
                      {formatDistanceToNow(new Date(comment.published_at), {
                        addSuffix: true,
                        locale: ru,
                      })}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button asChild variant="ghost" size="icon">
                        <Link
                          href={`https://vk.com/wall-${comment.group?.vk_id}_${comment.post_vk_id}?reply=${comment.vk_id}`}
                          target="_blank"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {hasNextPage && (
              <div className="pt-4 text-center">
                <Button
                  onClick={() => fetchNextPage()}
                  disabled={isFetchingNextPage}
                >
                  {isFetchingNextPage ? 'Загрузка...' : 'Загрузить еще'}
                </Button>
              </div>
            )}
            {comments.length === 0 && !isFetching && (
              <div className="text-center py-10 text-slate-400">
                Комментарии не найдены.
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
