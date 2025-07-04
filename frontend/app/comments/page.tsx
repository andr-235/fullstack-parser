'use client'

import { useState, useMemo } from 'react'
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
import { formatRelativeTime } from '@/lib/utils'
import { Search, ExternalLink } from 'lucide-react'
import {
  VKCommentResponse,
  VKGroupResponse,
  KeywordResponse,
} from '@/types/api'

export default function CommentsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterGroup, setFilterGroup] = useState('all')
  const [filterKeyword, setFilterKeyword] = useState('all')

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteComments({
    text: searchTerm || undefined,
    group_id: filterGroup !== 'all' ? Number(filterGroup) : undefined,
    keyword_id: filterKeyword !== 'all' ? Number(filterKeyword) : undefined,
  })

  const { data: groupsData } = useGroups({})
  const { data: keywordsData } = useKeywords({})

  const allComments = useMemo(
    () => data?.pages.flatMap((page) => page.items) ?? [],
    [data]
  )

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Фильтры комментариев</CardTitle>
          <CardDescription>
            Используйте фильтры для поиска нужных комментариев.
          </CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <Input
              placeholder="Поиск по тексту..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pr-10"
            />
            <Search
              size={16}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
            />
          </div>
          <Select value={filterGroup} onValueChange={setFilterGroup}>
            <SelectTrigger>
              <SelectValue placeholder="Фильтр по группе" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все группы</SelectItem>
              {groupsData?.items.map((group: VKGroupResponse) => (
                <SelectItem key={group.id} value={String(group.id)}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={filterKeyword} onValueChange={setFilterKeyword}>
            <SelectTrigger>
              <SelectValue placeholder="Фильтр по ключевому слову" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все ключевые слова</SelectItem>
              {keywordsData?.items.map((keyword: KeywordResponse) => (
                <SelectItem key={keyword.id} value={String(keyword.id)}>
                  {keyword.word}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Найденные комментарии</CardTitle>
          <CardDescription>
            Список комментариев, найденных по вашим фильтрам.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center p-8">
              <LoadingSpinner />
            </div>
          ) : error ? (
            <div className="text-destructive p-4 text-center">
              Ошибка: {error.message}
            </div>
          ) : (
            <>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Автор</TableHead>
                      <TableHead>Комментарий</TableHead>
                      <TableHead>Группа</TableHead>
                      <TableHead>Дата</TableHead>
                      <TableHead>Ссылка</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {allComments.length > 0 ? (
                      allComments.map((comment: VKCommentResponse) => (
                        <TableRow key={comment.id}>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <Avatar>
                                <AvatarImage
                                  src={comment.author_photo_url}
                                  alt={comment.author_name}
                                />
                                <AvatarFallback>
                                  {comment.author_name?.substring(0, 1) || 'A'}
                                </AvatarFallback>
                              </Avatar>
                              <span className="font-medium">
                                {comment.author_name}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="max-w-md">
                            <p className="truncate hover:whitespace-normal">
                              {comment.text}
                            </p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {comment.matched_keywords?.map(
                                (kw: KeywordResponse) => (
                                  <Badge key={kw.id} variant="secondary">
                                    {kw.word}
                                  </Badge>
                                )
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{comment.group?.name || 'N/A'}</TableCell>
                          <TableCell>
                            {formatRelativeTime(comment.created_at)}
                          </TableCell>
                          <TableCell>
                            <Button variant="ghost" size="icon" asChild>
                              <a
                                href={`https://vk.com/wall-${comment.group?.vk_id}_${comment.post_vk_id}?reply=${comment.vk_id}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center">
                          Комментарии не найдены.
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
              {hasNextPage && (
                <div className="mt-4 text-center">
                  <Button
                    onClick={() => fetchNextPage()}
                    disabled={isFetchingNextPage}
                  >
                    {isFetchingNextPage ? <LoadingSpinner /> : 'Загрузить еще'}
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
