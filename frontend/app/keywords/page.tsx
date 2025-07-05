'use client'

import { useState } from 'react'
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
} from 'lucide-react'
import {
  useKeywords,
  useKeywordCategories,
  useCreateKeyword,
  useUpdateKeyword,
  useDeleteKeyword,
} from '@/hooks/use-keywords'
import type { KeywordResponse } from '@/types/api'

const formatNumber = (num: number) => {
  return new Intl.NumberFormat('ru-RU').format(num)
}

export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [activeOnly, setActiveOnly] = useState(false)
  const [newKeyword, setNewKeyword] = useState('')

  const {
    data: keywordsData,
    isLoading,
    error,
  } = useKeywords({
    q: searchTerm || undefined,
    category: selectedCategory || undefined,
    active_only: activeOnly,
    limit: 100,
  })

  const { data: categoriesData } = useKeywordCategories()
  const createKeyword = useCreateKeyword()
  const updateKeyword = useUpdateKeyword()
  const deleteKeyword = useDeleteKeyword()

  // TODO: Implement client-side search until backend is ready
  const keywords =
    keywordsData?.items?.filter(
      (k) =>
        k.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
        k.category?.toLowerCase().includes(searchTerm.toLowerCase())
    ) || []

  const categories = Array.isArray(categoriesData) ? categoriesData : []

  const totalKeywords = keywordsData?.total || 0
  const activeKeywords =
    keywordsData?.items?.filter((k) => k.is_active).length || 0
  const totalMatches =
    keywordsData?.items?.reduce((sum, k) => sum + k.total_matches, 0) || 0

  const handleToggleActive = (keyword: KeywordResponse) => {
    updateKeyword.mutate({
      keywordId: keyword.id,
      data: { is_active: !keyword.is_active },
    })
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

  // Edit keyword word (simple prompt based editing)
  const handleEditKeyword = (keyword: KeywordResponse) => {
    const newWord = window.prompt('Изменить ключевое слово:', keyword.word)
    if (newWord && newWord.trim() && newWord.trim() !== keyword.word) {
      updateKeyword.mutate({
        keywordId: keyword.id,
        data: { word: newWord.trim() },
      })
    }
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
              <KeyRound className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Активных</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatNumber(activeKeywords)}
                </p>
              </div>
              <Play className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Категорий</p>
                <p className="text-2xl font-bold text-purple-600">
                  {formatNumber(categories.length)}
                </p>
              </div>
              <Tag className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Совпадений</p>
                <p className="text-2xl font-bold text-orange-600">
                  {formatNumber(totalMatches)}
                </p>
              </div>
              <Search className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters & List */}
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
                        <h3 className="font-semibold">{keyword.word}</h3>
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
                      size="sm"
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

                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleEditKeyword(keyword)}
                      disabled={
                        updateKeyword.isPending &&
                        updateKeyword.variables?.keywordId === keyword.id
                      }
                    >
                      <Edit className="h-4 w-4" />
                    </Button>

                    <Button
                      size="sm"
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
