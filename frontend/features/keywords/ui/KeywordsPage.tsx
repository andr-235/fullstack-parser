'use client'

import React, { useState } from 'react'
import {
  useKeywords,
  useCreateKeyword,
  useUpdateKeyword,
  useDeleteKeyword,
  useInfiniteKeywords,
} from '@/features/keywords/hooks/use-keywords'
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
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Plus, Trash2, Search, Check, X } from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { KeywordResponse, KeywordUpdate } from '@/types/api'
import useDebounce from '@/hooks/use-debounce'
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { useKeywordCategories } from '@/hooks/use-keywords'
import { cn } from '@/lib/utils'

const KeywordRow = ({
  keyword,
  onUpdate,
  onDelete,
  isUpdating,
  isDeleting,
}: {
  keyword: KeywordResponse
  onUpdate: (
    id: number,
    data: KeywordUpdate,
    callbacks?: { onSuccess?: () => void; onError?: () => void }
  ) => void
  onDelete: (id: number) => void
  isUpdating: boolean
  isDeleting: boolean
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedWord, setEditedWord] = useState(keyword.word)
  const debouncedWord = useDebounce(editedWord, 500)

  React.useEffect(() => {
    if (isEditing && debouncedWord !== keyword.word) {
      onUpdate(keyword.id, { word: debouncedWord })
    }
  }, [debouncedWord, isEditing, keyword.id, keyword.word, onUpdate])

  const handleSave = () => {
    if (editedWord !== keyword.word) {
      onUpdate(
        keyword.id,
        { word: editedWord },
        { onSuccess: () => {}, onError: () => {} }
      )
    }
    setIsEditing(false)
  }

  return (
    <TableRow
      key={keyword.id}
      className={!keyword.is_active ? 'opacity-50 bg-slate-50' : ''}
    >
      <TableCell className="py-2 px-3">
        {isEditing ? (
          <div className="flex items-center gap-2">
            <Input
              value={editedWord}
              onChange={(e) => setEditedWord(e.target.value)}
              className="h-8 text-sm border-slate-300"
              aria-label="Редактировать ключевое слово"
              autoFocus
            />
            <Button
              size="icon"
              className="h-8 w-8"
              onClick={handleSave}
              aria-label="Сохранить"
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8"
              onClick={() => setIsEditing(false)}
              aria-label="Отмена"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <span
            className="cursor-pointer group-hover:underline"
            onClick={() => setIsEditing(true)}
            title="Нажмите, чтобы редактировать"
            tabIndex={0}
            role="button"
            aria-label="Редактировать ключевое слово"
          >
            {keyword.word}
            {!keyword.is_active && (
              <span
                className="ml-2 text-xs text-slate-400"
                title="Ключевое слово неактивно"
              >
                (неактивно)
              </span>
            )}
          </span>
        )}
      </TableCell>
      <TableCell className="py-2 px-3 text-center">
        <Badge
          variant="secondary"
          className="font-mono text-xs bg-slate-100 text-slate-700 border border-slate-200"
        >
          {keyword.total_matches}
        </Badge>
      </TableCell>
      <TableCell className="py-2 px-3 text-center">
        <Switch
          checked={keyword.is_active}
          onCheckedChange={(isActive) => {
            onUpdate(keyword.id, { is_active: isActive })
          }}
          disabled={isUpdating}
          aria-label="Статус активности"
        />
      </TableCell>
      <TableCell className="py-2 px-3 text-right">
        <Button
          variant="ghost"
          size="icon"
          className="text-red-500 hover:text-red-400"
          onClick={() => onDelete(keyword.id)}
          disabled={isDeleting}
          aria-label="Удалить ключевое слово"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </TableCell>
    </TableRow>
  )
}

export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [newKeyword, setNewKeyword] = useState('')
  const [activeOnly, setActiveOnly] = useState(true)
  const [category, setCategory] = useState<string>('')

  // Для тестов: если категория не выбрана, не передавать параметр category
  const pageSize = 20
  const {
    data,
    isLoading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteKeywords({
    q: searchTerm,
    active_only: activeOnly,
    category: category || undefined,
    pageSize,
    order_by: 'word',
    order_dir: 'asc',
  })

  const keywords = data?.pages.flatMap((page) => page.items) || []
  const total = data?.pages[0]?.total || 0
  const active = keywords.filter((k) => k.is_active).length || 0
  const totalMatches =
    keywords.reduce((sum, k) => sum + k.total_matches, 0) || 0

  // Intersection Observer для бесконечного скролла
  const loaderRef = React.useRef<HTMLTableRowElement | null>(null)
  React.useEffect(() => {
    if (!hasNextPage || isFetchingNextPage) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) fetchNextPage()
      },
      { root: null, rootMargin: '0px', threshold: 1.0 }
    )
    if (loaderRef.current) observer.observe(loaderRef.current)
    return () => {
      if (loaderRef.current) observer.unobserve(loaderRef.current)
    }
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const { data: categoriesData } = useKeywordCategories()
  const createKeywordMutation = useCreateKeyword()
  const updateKeywordMutation = useUpdateKeyword()
  const deleteKeywordMutation = useDeleteKeyword()

  const handleAddKeyword = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newKeyword.trim()) return
    createKeywordMutation.mutate(
      {
        word: newKeyword,
        is_active: true,
        is_case_sensitive: false,
        is_whole_word: false,
        category: category || 'Без категории',
      },
      {
        onSuccess: () => setNewKeyword(''),
      }
    )
  }

  const handleDeleteKeyword = (id: number) => {
    if (window.confirm('Удалить ключевое слово?')) {
      deleteKeywordMutation.mutate(id)
    }
  }

  const handleUpdateKeyword = (
    id: number,
    data: KeywordUpdate,
    callbacks?: { onSuccess?: () => void; onError?: () => void }
  ) => {
    if (callbacks) {
      updateKeywordMutation.mutate({ keywordId: id, data }, callbacks)
    } else {
      updateKeywordMutation.mutateAsync({ keywordId: id, data })
    }
  }

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner />
        </div>
      )
    }
    if (isError) {
      return (
        <div className="text-center text-red-500 py-10">
          <p>Ошибка загрузки</p>
          <p>{(error as Error)?.message}</p>
        </div>
      )
    }
    return (
      <div className="max-h-[400px] overflow-y-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ключевое слово</TableHead>
              <TableHead>Найдено комментариев</TableHead>
              <TableHead>Статус</TableHead>
              <TableHead className="text-right">Действия</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keywords?.map((keyword) => (
              <KeywordRow
                key={keyword.id}
                keyword={keyword}
                onUpdate={handleUpdateKeyword}
                onDelete={handleDeleteKeyword}
                isUpdating={updateKeywordMutation.isPending}
                isDeleting={deleteKeywordMutation.isPending}
              />
            ))}
          </TableBody>
        </Table>
      </div>
    )
  }

  return (
    <Card className="border border-slate-200 shadow-none rounded-xl bg-white">
      <CardHeader className="pb-2 border-b border-slate-100">
        <h1 className="text-lg font-bold tracking-tight font-mono text-slate-800">
          Ключевые слова
        </h1>
        <CardDescription className="text-xs text-slate-500">
          Управляйте ключевыми словами для поиска в комментариях. Всё строго,
          как на допросе.
        </CardDescription>
        <div className="flex flex-wrap gap-3 pt-2 items-end">
          <div className="flex flex-col gap-1 min-w-[180px]">
            <Label htmlFor="search" className="text-xs font-medium">
              Поиск
            </Label>
            <div className="relative">
              <Input
                id="search"
                placeholder="Поиск по словам..."
                className="pl-9 h-8 text-sm border-slate-300"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                aria-label="Поиск по ключевым словам"
              />
              <Search className="absolute left-2 top-2 h-4 w-4 text-slate-400" />
            </div>
          </div>
          <div className="flex flex-col gap-1 min-w-[140px]">
            <Label htmlFor="category" className="text-xs font-medium">
              Категория
            </Label>
            <Select
              value={category || 'all'}
              onValueChange={(v) => setCategory(v === 'all' ? '' : v)}
            >
              <SelectTrigger
                id="category"
                className="w-36 h-8 text-sm border-slate-300"
              >
                <SelectValue placeholder="Все категории" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Все категории</SelectItem>
                {(categoriesData || []).map((cat: string) => (
                  <SelectItem key={cat} value={cat}>
                    {cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2 min-w-[120px]">
            <Switch
              id="activeOnly"
              checked={activeOnly}
              onCheckedChange={setActiveOnly}
              aria-label="Только активные"
            />
            <Label htmlFor="activeOnly" className="text-xs font-medium">
              Только активные
            </Label>
          </div>
          <Button
            variant="outline"
            className="h-8 text-xs border-slate-300"
            onClick={() => {
              setSearchTerm('')
              setCategory('')
              setActiveOnly(true)
            }}
            aria-label="Сбросить фильтры"
          >
            Сбросить фильтры
          </Button>
        </div>
        <div className="flex gap-4 pt-2 text-xs text-slate-400 font-mono">
          <span>
            Всего: <b className="text-slate-700">{total}</b>
          </span>
          <span>
            Активных: <b className="text-slate-700">{active}</b>
          </span>
          <span>
            Найдено: <b className="text-slate-700">{totalMatches}</b>
          </span>
        </div>
        <div className="space-x-2 flex pt-2">
          <form
            onSubmit={handleAddKeyword}
            className="flex items-center gap-2 w-full"
          >
            <Input
              placeholder="Новое ключевое слово"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              disabled={createKeywordMutation.isPending}
              className="h-8 text-sm border-slate-300"
              aria-label="Новое ключевое слово"
            />
            <Button
              type="submit"
              disabled={createKeywordMutation.isPending}
              className="h-8 text-xs"
            >
              <Plus className="h-4 w-4 mr-1" />
              Добавить
            </Button>
          </form>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="max-h-[400px] overflow-y-auto border border-slate-100 rounded-lg">
          <Table className="text-sm">
            <TableHeader>
              <TableRow className="bg-slate-50">
                <TableHead className="py-2 px-3">Ключевое слово</TableHead>
                <TableHead className="py-2 px-3 text-center">Найдено</TableHead>
                <TableHead className="py-2 px-3 text-center">Статус</TableHead>
                <TableHead className="py-2 px-3 text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell
                    colSpan={4}
                    className="text-center py-8"
                    role="status"
                  >
                    <LoadingSpinner />
                  </TableCell>
                </TableRow>
              ) : isError ? (
                <TableRow>
                  <TableCell
                    colSpan={4}
                    className="text-center text-red-500 py-8"
                  >
                    <div>Ошибка загрузки</div>
                  </TableCell>
                </TableRow>
              ) : keywords.length ? (
                <>
                  {keywords.map((keyword, idx) => (
                    <KeywordRow
                      key={keyword.id}
                      keyword={keyword}
                      onUpdate={handleUpdateKeyword}
                      onDelete={handleDeleteKeyword}
                      isUpdating={updateKeywordMutation.isPending}
                      isDeleting={deleteKeywordMutation.isPending}
                    />
                  ))}
                  <TableRow ref={loaderRef}>
                    <TableCell colSpan={4} className="text-center py-4">
                      {isFetchingNextPage && <LoadingSpinner />}
                      {!hasNextPage && 'Все ключевые слова загружены'}
                    </TableCell>
                  </TableRow>
                </>
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={4}
                    className="text-center text-slate-400 py-8"
                  >
                    Нет ключевых слов. Добавь первое — и будет как в отделе по
                    борьбе с преступностью: всё под контролем.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
