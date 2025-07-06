'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { LoadingSpinnerWithText } from '@/components/ui/loading-spinner'
import {
  Plus,
  KeyRound,
  Search,
  Filter,
  Edit,
  Trash2,
  Play,
  Pause,
  Upload,
  Download,
  Tag,
  AlertCircle,
  XCircle,
} from 'lucide-react'
import {
  useKeywords,
  useKeywordCategories,
  useCreateKeyword,
  useUpdateKeyword,
  useDeleteKeyword,
} from '@/hooks/use-keywords'
import useDebounce from '@/hooks/use-debounce'
import type { KeywordResponse } from '@/types/api'

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('ru-RU').format(num)
}

export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [activeOnly, setActiveOnly] = useState(true)
  const [newKeyword, setNewKeyword] = useState('')

  const debouncedSearchTerm = useDebounce(searchTerm, 300)

  // Inline edit state
  const [editingKeywordId, setEditingKeywordId] = useState<number | null>(null)
  const [editWord, setEditWord] = useState('')

  const {
    data: keywordsData,
    isLoading,
    error,
  } = useKeywords({
    q: debouncedSearchTerm || undefined,
    category: selectedCategory || undefined,
    active_only: activeOnly,
    limit: 100,
  })

  const { data: categoriesData } = useKeywordCategories()
  const createKeyword = useCreateKeyword()
  const updateKeyword = useUpdateKeyword()
  const deleteKeyword = useDeleteKeyword()

  const keywords = keywordsData?.items || []
  const categories = Array.isArray(categoriesData) ? categoriesData : []

  const totalKeywords = keywordsData?.total || 0
  const activeKeywords =
    keywordsData?.items?.filter((k) => k.is_active).length || 0
  const totalMatches =
    keywordsData?.items?.reduce((sum, k) => sum + k.total_matches, 0) || 0

  const handleToggleActive = (keyword: KeywordResponse) => {
    updateKeyword.mutate(
      {
        keywordId: keyword.id,
        data: { is_active: !keyword.is_active },
      },
      {
        onSuccess: () => {
          toast.success(
            `Ключевое слово «${keyword.word}» теперь ${
              keyword.is_active ? 'неактивно' : 'активно'
            }`
          )
        },
        onError: (err: Error) => toast.error(err.message),
      }
    )
  }

  const handleDeleteKeyword = (keywordId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить это ключевое слово?')) {
      deleteKeyword.mutate(keywordId)
    }
  }

  const handleAddKeyword = () => {
    if (!newKeyword.trim()) return
    createKeyword.mutate(
      {
        word: newKeyword,
        is_active: true,
        is_case_sensitive: false,
        is_whole_word: false,
        category: 'Без категории',
      },
      {
        onSuccess: () => {
          setNewKeyword('')
        },
      }
    )
  }

  // Start editing selected keyword (enter edit mode)
  const handleStartEditing = (keyword: KeywordResponse) => {
    setEditingKeywordId(keyword.id)
    setEditWord(keyword.word)
  }

  // Cancel editing
  const handleCancelEditing = () => {
    setEditingKeywordId(null)
    setEditWord('')
  }

  // Save changes
  const handleSaveKeyword = (keywordId: number) => {
    if (!editWord.trim()) {
      toast.error('Ключевое слово не может быть пустым')
      return
    }
    if (editWord.trim().length < 2) {
      toast.error('Ключевое слово слишком короткое')
      return
    }

    toast
      .promise(
        updateKeyword.mutateAsync({
          keywordId,
          data: { word: editWord.trim() },
        }),
        {
          loading: 'Сохраняем…',
          success: 'Сохранено',
          error: (err: Error) => err.message,
        }
      )
      .then(() => {
        setEditingKeywordId(null)
        setEditWord('')
      })
  }

  const handleClearFilters = () => {
    setSearchTerm('')
    setSelectedCategory('')
    setActiveOnly(true)
  }

  if (isLoading && !keywordsData) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinnerWithText text="Загрузка ключевых слов..." size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center text-red-500">
          <AlertCircle className="mx-auto h-12 w-12" />
          <h3 className="mt-4 text-lg font-medium">Ошибка загрузки</h3>
          <p className="mt-1 text-sm text-gray-600">{error.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-50">
            Ключевые слова
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Управление ключевыми словами для поиска в комментариях VK
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Импорт
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Экспорт
          </Button>
        </div>
      </div>

      {/* Add new keyword */}
      <Card>
        <CardContent className="p-4">
          <div className="flex w-full items-center space-x-2">
            <Input
              type="text"
              placeholder="Новое ключевое слово..."
              className="flex-1"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddKeyword()}
            />
            <Button
              onClick={handleAddKeyword}
              disabled={createKeyword.isPending}
            >
              {createKeyword.isPending ? (
                <LoadingSpinnerWithText text="" size="sm" />
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Добавить
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Всего слов</p>
                <p className="text-2xl font-bold">
                  {formatNumber(totalKeywords)}
                </p>
              </div>
              <KeyRound className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Активных</p>
                <p className="text-2xl font-bold">
                  {formatNumber(activeKeywords)}
                </p>
              </div>
              <Play className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Совпадений</p>
                <p className="text-2xl font-bold">
                  {formatNumber(totalMatches)}
                </p>
              </div>
              <Tag className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Категорий</p>
                <p className="text-2xl font-bold">
                  {formatNumber(categories.length)}
                </p>
              </div>
              <Filter className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4 space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-grow">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <Input
                type="text"
                placeholder="Поиск по словам и категориям..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Switch
                  id="active-only"
                  checked={activeOnly}
                  onCheckedChange={setActiveOnly}
                />
                <Label htmlFor="active-only">Только активные</Label>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleClearFilters}
                disabled={!searchTerm && !selectedCategory && activeOnly}
              >
                <XCircle className="h-4 w-4 mr-2" />
                Сбросить
              </Button>
            </div>
          </div>
          {categories.length > 0 && (
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-sm font-medium text-gray-600">
                Категории:
              </span>
              {categories.map((category) => (
                <Badge
                  key={category}
                  variant={
                    selectedCategory === category ? 'default' : 'secondary'
                  }
                  onClick={() =>
                    setSelectedCategory(
                      selectedCategory === category ? '' : category
                    )
                  }
                  className="cursor-pointer"
                >
                  {category}
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Keywords table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder="Поиск по ключевому слову или категории..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            {/* Category Filter */}
            <div className="sm:w-48">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full h-10 px-3 border bg-background border-input rounded-md text-sm"
              >
                <option value="">Все категории</option>
                {categories.map((category: string) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>

            {/* Active Only Filter */}
            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={activeOnly}
                  onChange={(e) => setActiveOnly(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">Только активные</span>
              </label>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {isLoading ? (
              <LoadingSpinnerWithText text="Обновление списка..." />
            ) : keywords.length > 0 ? (
              keywords.map((keyword) => (
                <div
                  key={keyword.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-500 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        {editingKeywordId === keyword.id ? (
                          <Input
                            value={editWord}
                            onChange={(e) => setEditWord(e.target.value)}
                            className="w-48"
                          />
                        ) : (
                          <h3 className="font-semibold">{keyword.word}</h3>
                        )}
                        <Badge
                          variant={keyword.is_active ? 'success' : 'secondary'}
                        >
                          {keyword.is_active ? 'Активно' : 'Неактивно'}
                        </Badge>
                        <Badge variant="outline">{keyword.category}</Badge>
                        {keyword.is_case_sensitive && (
                          <Badge variant="warning">С учетом регистра</Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">
                        Совпадений: {formatNumber(keyword.total_matches)} •
                        Создано:{' '}
                        {new Date(keyword.created_at).toLocaleDateString(
                          'ru-RU'
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1">
                    <Button
                      size="icon"
                      variant={keyword.is_active ? 'secondary' : 'default'}
                      onClick={() => handleToggleActive(keyword)}
                      disabled={
                        updateKeyword.isPending &&
                        updateKeyword.variables?.keywordId === keyword.id
                      }
                    >
                      {keyword.is_active ? (
                        <Pause className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>

                    {editingKeywordId === keyword.id ? (
                      <>
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleSaveKeyword(keyword.id)}
                          disabled={
                            updateKeyword.isPending &&
                            updateKeyword.variables?.keywordId === keyword.id
                          }
                        >
                          {updateKeyword.isPending &&
                          updateKeyword.variables?.keywordId === keyword.id ? (
                            <LoadingSpinnerWithText text="" size="sm" />
                          ) : (
                            'Сохранить'
                          )}
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={handleCancelEditing}
                        >
                          Отмена
                        </Button>
                      </>
                    ) : (
                      <Button
                        size="icon"
                        variant="ghost"
                        onClick={() => handleStartEditing(keyword)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    )}

                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => handleDeleteKeyword(keyword.id)}
                      className="text-red-600 hover:text-red-700"
                      disabled={
                        deleteKeyword.isPending &&
                        deleteKeyword.variables === keyword.id
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <KeyRound className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold">
                  Ключевые слова не найдены
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || selectedCategory
                    ? 'Измените критерии поиска или очистите фильтры'
                    : 'Добавьте первое ключевое слово для начала мониторинга'}
                </p>
                <Button onClick={handleAddKeyword}>
                  <Plus className="h-4 w-4 mr-2" />
                  Добавить ключевое слово
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
