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
} from 'lucide-react'
import { useKeywords } from '@/hooks/use-keywords'

// Пока используем моковые данные, потом подключим React Query
const mockKeywords = [
  {
    id: 1,
    word: 'купить',
    category: 'Коммерция',
    is_active: true,
    case_sensitive: false,
    created_at: '2024-01-15T10:00:00Z',
    matches_count: 156,
  },
  {
    id: 2,
    word: 'продам',
    category: 'Коммерция',
    is_active: true,
    case_sensitive: false,
    created_at: '2024-01-15T10:00:00Z',
    matches_count: 89,
  },
  {
    id: 3,
    word: 'работа',
    category: 'Трудоустройство',
    is_active: true,
    case_sensitive: false,
    created_at: '2024-01-14T15:30:00Z',
    matches_count: 234,
  },
  {
    id: 4,
    word: 'вакансия',
    category: 'Трудоустройство',
    is_active: false,
    case_sensitive: false,
    created_at: '2024-01-14T15:30:00Z',
    matches_count: 67,
  },
  {
    id: 5,
    word: 'услуги',
    category: 'Сервисы',
    is_active: true,
    case_sensitive: false,
    created_at: '2024-01-13T09:15:00Z',
    matches_count: 123,
  },
]

const mockCategories = [
  'Коммерция',
  'Трудоустройство',
  'Сервисы',
  'Недвижимость',
  'Транспорт',
]

export default function KeywordsPage() {
  const { data: keywords, isLoading, error } = useKeywords()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [activeOnly, setActiveOnly] = useState(true)
  const [newKeyword, setNewKeyword] = useState('')

  // Фильтрация ключевых слов
  const filteredKeywords = mockKeywords.filter((keyword) => {
    const matchesSearch =
      keyword.word.toLowerCase().includes(searchTerm.toLowerCase()) ||
      keyword.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory =
      !selectedCategory || keyword.category === selectedCategory
    const matchesActive = !activeOnly || keyword.is_active

    return matchesSearch && matchesCategory && matchesActive
  })

  const totalKeywords = mockKeywords.length
  const activeKeywords = mockKeywords.filter((k) => k.is_active).length
  const totalMatches = mockKeywords.reduce((sum, k) => sum + k.matches_count, 0)

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ru-RU').format(num)
  }

  const handleToggleActive = (keywordId: number) => {
    // TODO: Реализовать через React Query
    console.log('Toggle keyword:', keywordId)
  }

  const handleDeleteKeyword = (keywordId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить это ключевое слово?')) {
      // TODO: Реализовать через React Query
      console.log('Delete keyword:', keywordId)
    }
  }

  const handleAddKeyword = () => {
    // TODO: Implement add keyword logic
    console.log('Adding keyword:', newKeyword)
    setNewKeyword('')
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinnerWithText text="Загрузка ключевых слов..." size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ключевые слова</h1>
          <p className="text-gray-600 mt-2">
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
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Добавить
          </Button>
        </div>
      </div>

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
                  {formatNumber(mockCategories.length)}
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

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по ключевому слову или категории..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div className="sm:w-48">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Все категории</option>
                {mockCategories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>

            {/* Active Only Filter */}
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-600" />
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={activeOnly}
                  onChange={(e) => setActiveOnly(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Только активные</span>
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Keywords List */}
      <Card>
        <CardHeader>
          <CardTitle>
            Ключевые слова ({formatNumber(filteredKeywords.length)})
          </CardTitle>
          <CardDescription>
            {searchTerm && `Результаты поиска для "${searchTerm}"`}
            {selectedCategory && ` в категории "${selectedCategory}"`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredKeywords.length > 0 ? (
            <div className="space-y-3">
              {filteredKeywords.map((keyword) => (
                <div
                  key={keyword.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold text-gray-900">
                          {keyword.word}
                        </h3>
                        <Badge
                          variant={keyword.is_active ? 'success' : 'secondary'}
                          className="text-xs"
                        >
                          {keyword.is_active ? 'Активно' : 'Неактивно'}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {keyword.category}
                        </Badge>
                        {keyword.case_sensitive && (
                          <Badge variant="warning" className="text-xs">
                            С учетом регистра
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        Совпадений: {formatNumber(keyword.matches_count)} •
                        Создано:{' '}
                        {new Date(keyword.created_at).toLocaleDateString(
                          'ru-RU'
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant={keyword.is_active ? 'secondary' : 'default'}
                      onClick={() => handleToggleActive(keyword.id)}
                    >
                      {keyword.is_active ? (
                        <>
                          <Pause className="h-3 w-3 mr-1" />
                          Отключить
                        </>
                      ) : (
                        <>
                          <Play className="h-3 w-3 mr-1" />
                          Включить
                        </>
                      )}
                    </Button>

                    <Button size="sm" variant="ghost">
                      <Edit className="h-3 w-3 mr-1" />
                      Изменить
                    </Button>

                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDeleteKeyword(keyword.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <KeyRound className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ключевые слова не найдены
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm || selectedCategory
                  ? 'Измените критерии поиска или очистите фильтры'
                  : 'Добавьте первое ключевое слово для начала мониторинга'}
              </p>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Добавить ключевое слово
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Category Management */}
      <Card>
        <CardHeader>
          <CardTitle>Управление категориями</CardTitle>
          <CardDescription>
            Создавайте и управляйте категориями для организации ключевых слов
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {mockCategories.map((category) => {
              const categoryCount = mockKeywords.filter(
                (k) => k.category === category
              ).length
              return (
                <Badge key={category} variant="outline" className="px-3 py-1">
                  {category} ({categoryCount})
                </Badge>
              )
            })}
            <Button size="sm" variant="ghost" className="px-3 py-1 h-auto">
              <Plus className="h-3 w-3 mr-1" />
              Добавить категорию
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Добавить новое ключевое слово</h2>
          <div className="form-control flex-row gap-2">
            <input
              type="text"
              placeholder="Введите ключевое слово"
              className="input input-bordered w-full"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleAddKeyword}>
              <Plus size={18} />
              Добавить
            </button>
          </div>
        </div>
      </div>

      <div className="card bg-base-100 shadow">
        <div className="card-body">
          <h2 className="card-title">Список ключевых слов</h2>
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="flex justify-center p-8">
                <span className="loading loading-spinner loading-lg"></span>
              </div>
            ) : error ? (
              <div role="alert" className="alert alert-error">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="stroke-current shrink-0 h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span>Ошибка: {error.message}</span>
              </div>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Ключевое слово</th>
                    <th>Кол-во упоминаний</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {keywords?.map((keyword) => (
                    <tr key={keyword.id}>
                      <td>{keyword.id}</td>
                      <td>
                        <span className="badge badge-lg">
                          {keyword.keyword}
                        </span>
                      </td>
                      <td>
                        <div className="badge badge-ghost">
                          {keyword.matches_count}
                        </div>
                      </td>
                      <td className="flex gap-2">
                        <button className="btn btn-ghost btn-xs">
                          <Edit size={16} />
                        </button>
                        <button className="btn btn-ghost btn-xs text-error">
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
