'use client'

import React, { useState } from 'react'
import {
  useKeywords,
  useCreateKeyword,
  useUpdateKeyword,
  useDeleteKeyword,
  useInfiniteKeywords,
  useUpdateKeywordsStats,
  useTotalMatches,
} from '@/features/keywords/hooks/use-keywords'
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
import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { LoadingSpinner } from '@/shared/ui'
import {
  Plus,
  Trash2,
  Search,
  Check,
  X,
  Hash,
  Target,
  MessageSquare,
  Activity,
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { KeywordResponse, KeywordUpdate } from '@/types/api'
import { useDebounce } from '@/shared/hooks'
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from '@/shared/ui'
import { Label } from '@/shared/ui'
import { useKeywordCategories } from '@/entities/keyword'
import { cn } from '@/shared/lib/utils'
import UploadKeywordsModal from './UploadKeywordsModal'

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
        { onSuccess: () => { }, onError: () => { } }
      )
    }
    setIsEditing(false)
  }

  return (
    <TableRow
      className="group-row animate-fade-in-up transition-all duration-300 hover:bg-gradient-to-r hover:from-slate-700 hover:to-slate-600 hover:shadow-md transform hover:scale-[1.01]"
      style={{ animationDelay: `${keyword.id * 20}ms` }}
    >
      <TableCell>
        {isEditing ? (
          <div className="flex items-center gap-2">
            <Input
              value={editedWord}
              onChange={(e) => setEditedWord(e.target.value)}
              autoFocus
              className="border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500"
            />
            <Button
              size="icon"
              onClick={handleSave}
              className="bg-green-600 hover:bg-green-700"
            >
              <Check className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              onClick={() => {
                setEditedWord(keyword.word)
                setIsEditing(false)
              }}
              className="hover:bg-red-900 text-red-400 hover:text-red-300"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Hash className="h-4 w-4 text-white" />
            </div>
            <span
              className="font-medium text-slate-200 cursor-pointer hover:text-blue-400 transition-colors"
              onClick={() => setIsEditing(true)}
            >
              {keyword.word}
            </span>
          </div>
        )}
      </TableCell>
      <TableCell>
        <span className="text-slate-400 text-sm">
          {keyword.category || '—'}
        </span>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-blue-400" />
          <span className="font-semibold text-blue-400">
            {keyword.total_matches}
          </span>
        </div>
      </TableCell>
      <TableCell>
        <span
          className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold shadow-sm transition-all duration-200 ${keyword.is_active ? 'bg-gradient-to-r from-green-900 to-emerald-900 text-green-300 hover:from-green-800 hover:to-emerald-800' : 'bg-gradient-to-r from-slate-700 to-gray-700 text-slate-400 hover:from-slate-600 hover:to-gray-600'}`}
        >
          <span
            className={`w-2 h-2 rounded-full ${keyword.is_active ? 'bg-green-400 animate-pulse' : 'bg-slate-500'}`}
          ></span>
          {keyword.is_active ? 'Активно' : 'Неактивно'}
        </span>
      </TableCell>
      <TableCell className="text-right">
        <div className="flex items-center justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            aria-label="удалить"
            className="hover:bg-red-900 text-red-400 hover:text-red-300 transition-all duration-200 hover:scale-110"
            disabled={isDeleting}
            onClick={() => onDelete(keyword.id)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </TableCell>
    </TableRow>
  )
}

export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [newKeyword, setNewKeyword] = useState('')
  const [newKeywordCategory, setNewKeywordCategory] = useState('')
  const [activeOnly, setActiveOnly] = useState(true)
  const [category, setCategory] = useState<string>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(1000) // Увеличиваем лимит для загрузки большего количества записей

  // Пагинация
  const { data, isLoading, error, refetch } = useKeywords({
    q: searchTerm,
    active_only: activeOnly,
    category: category || undefined,
    page: currentPage,
    size: itemsPerPage,
  })

  const keywords = data?.items || []
  const total = data?.total || 0
  const active = keywords.filter((k) => k.is_active).length || 0

  // Получаем общее количество совпадений
  const { data: totalMatchesData } = useTotalMatches()
  const totalMatches = totalMatchesData?.total_matches || 0

  // Сброс страницы при изменении фильтров
  React.useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, activeOnly, category])

  const totalPages = Math.ceil(total / itemsPerPage)

  const { data: categoriesData } = useKeywordCategories()
  const createKeywordMutation = useCreateKeyword()
  const updateKeywordMutation = useUpdateKeyword()
  const deleteKeywordMutation = useDeleteKeyword()
  const updateStatsMutation = useUpdateKeywordsStats()

  // Автоматически обновляем статистику при загрузке страницы
  React.useEffect(() => {
    updateStatsMutation.mutate()
  }, [])

  const handleAddKeyword = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newKeyword.trim()) return
    createKeywordMutation.mutate(
      {
        word: newKeyword,
        is_active: true,
        is_case_sensitive: false,
        is_whole_word: false,
        category: newKeywordCategory.trim() || undefined,
      },
      {
        onSuccess: () => {
          setNewKeyword('')
          setNewKeywordCategory('')
          toast.success('Ключевое слово добавлено! 🎯')
        },
      }
    )
  }

  const handleDeleteKeyword = (id: number) => {
    if (window.confirm('Удалить ключевое слово?')) {
      deleteKeywordMutation.mutate(id, {
        onSuccess: () => toast.success('Ключевое слово удалено! 🗑️'),
      })
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

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-white/10 rounded-lg">
            <Target className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-bold">Управление ключевыми словами</h1>
        </div>
        <p className="text-slate-300">
          Добавляйте, настраивайте и управляйте ключевыми словами для поиска в
          комментариях
        </p>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <Hash className="h-5 w-5 text-purple-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Всего слов</p>
                <p className="text-2xl font-bold text-purple-400">{total}</p>
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
                <p className="text-2xl font-bold text-green-400">{active}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-slate-800 to-slate-700 border-slate-600 hover:shadow-lg transition-shadow duration-300">
          <CardContent className="p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-slate-700 rounded-lg">
                <MessageSquare className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-300">Найдено</p>
                <p className="text-2xl font-bold text-blue-400">
                  {totalMatches}
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
            Управление ключевыми словами
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Поиск и фильтры */}
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Поиск по ключевым словам..."
                className="pl-10 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm text-slate-300">
                <Switch
                  checked={activeOnly}
                  onCheckedChange={setActiveOnly}
                  className="data-[state=checked]:bg-blue-600"
                />
                <span>Только активные</span>
              </label>

              <Select
                value={category || 'all'}
                onValueChange={(v) => setCategory(v === 'all' ? '' : v)}
              >
                <SelectTrigger className="w-40 border-slate-600 bg-slate-700 text-slate-200">
                  <SelectValue placeholder="Все категории" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-600">
                  <SelectItem
                    value="all"
                    className="text-slate-200 hover:bg-slate-700"
                  >
                    Все категории
                  </SelectItem>
                  {(categoriesData || []).map((cat: string) => (
                    <SelectItem
                      key={cat}
                      value={cat}
                      className="text-slate-200 hover:bg-slate-700"
                    >
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <UploadKeywordsModal onSuccess={() => refetch()} />
            </div>
          </div>

          {/* Форма добавления */}
          <form onSubmit={handleAddKeyword} className="flex gap-2">
            <Input
              placeholder="Новое ключевое слово"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              disabled={createKeywordMutation.isPending}
              className="flex-1 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
            />
            <Input
              placeholder="Категория (необязательно)"
              value={newKeywordCategory}
              onChange={(e) => setNewKeywordCategory(e.target.value)}
              disabled={createKeywordMutation.isPending}
              className="w-40 border-slate-600 bg-slate-700 text-slate-200 focus:border-blue-500 focus:ring-blue-500 placeholder-slate-400"
            />
            <Button
              type="submit"
              disabled={createKeywordMutation.isPending}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 transition-all duration-200 hover:scale-105"
            >
              {createKeywordMutation.isPending ? (
                <LoadingSpinner className="h-4 w-4" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              <span className="ml-2">Добавить</span>
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Таблица ключевых слов */}
      <Card className="border-slate-700 bg-slate-800 shadow-lg">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full relative">
              <thead className="sticky top-0 z-10 bg-gradient-to-r from-slate-700 to-slate-600 shadow-md">
                <tr>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Ключевое слово
                  </th>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Категория
                  </th>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Найдено
                  </th>
                  <th className="px-4 py-3 text-left font-bold text-slate-200">
                    Статус
                  </th>
                  <th className="px-4 py-3 text-right font-bold text-slate-200">
                    Действия
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {isLoading ? (
                  <tr>
                    <td colSpan={5} className="text-center py-10">
                      <div className="flex flex-col items-center justify-center space-y-4">
                        <LoadingSpinner className="h-8 w-8 text-blue-500" />
                        <span className="text-slate-400 font-medium">
                          Загрузка ключевых слов...
                        </span>
                      </div>
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={5} className="text-center py-10">
                      <div className="flex flex-col items-center justify-center space-y-4">
                        <div className="w-16 h-16 bg-red-900 rounded-full flex items-center justify-center">
                          <X className="h-8 w-8 text-red-400" />
                        </div>
                        <p className="text-red-400 font-medium">
                          Ошибка загрузки
                        </p>
                        <p className="text-slate-400 text-sm">
                          {(error as Error)?.message}
                        </p>
                      </div>
                    </td>
                  </tr>
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
                  </>
                ) : (
                  <tr>
                    <td colSpan={5} className="text-center py-10">
                      <div className="flex flex-col items-center justify-center space-y-4">
                        <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center">
                          <Hash className="h-8 w-8 text-slate-400" />
                        </div>
                        <p className="text-slate-400 font-medium">
                          Нет ключевых слов
                        </p>
                        <p className="text-slate-500 text-sm">
                          Добавьте первое ключевое слово для начала работы
                        </p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Пагинация */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 bg-slate-750 border-t border-slate-700">
              <div className="text-sm text-slate-400">
                Показано {(currentPage - 1) * itemsPerPage + 1}-
                {Math.min(currentPage * itemsPerPage, total)} из {total}{' '}
                ключевых слов
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="border-slate-600 text-slate-300 hover:bg-slate-700"
                >
                  Назад
                </Button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (page) => (
                      <Button
                        key={page}
                        variant={page === currentPage ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setCurrentPage(page)}
                        className={
                          page === currentPage
                            ? 'bg-purple-600 hover:bg-purple-700'
                            : 'border-slate-600 text-slate-300 hover:bg-slate-700'
                        }
                      >
                        {page}
                      </Button>
                    )
                  )}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setCurrentPage(Math.min(totalPages, currentPage + 1))
                  }
                  disabled={currentPage === totalPages}
                  className="border-slate-600 text-slate-300 hover:bg-slate-700"
                >
                  Вперед
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
