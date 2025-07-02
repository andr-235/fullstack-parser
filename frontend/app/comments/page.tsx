'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinnerWithText } from '@/components/ui/loading-spinner'
import { 
  MessageSquare, 
  Search,
  Filter,
  ExternalLink,
  Calendar,
  User,
  Heart,
  MessageCircle,
  Eye,
  TrendingUp
} from 'lucide-react'

// Моковые данные комментариев
const mockComments = [
  {
    id: 1,
    text: 'Продам iPhone 13 в отличном состоянии! Цена договорная',
    author_name: 'Алексей Петров',
    author_id: 12345,
    group_name: 'Барахолка СПб',
    group_id: 67890,
    post_id: 111,
    comment_id: 222,
    created_at: '2024-01-15T14:30:00Z',
    likes_count: 5,
    replies_count: 2,
    matched_keywords: ['продам', 'iPhone'],
    vk_url: 'https://vk.com/wall-67890_111?reply=222'
  },
  {
    id: 2,
    text: 'Ищу работу программистом в IT компании',
    author_name: 'Мария Сидорова',
    author_id: 54321,
    group_name: 'IT Вакансии Москва',
    group_id: 98765,
    post_id: 333,
    comment_id: 444,
    created_at: '2024-01-15T13:15:00Z',
    likes_count: 12,
    replies_count: 7,
    matched_keywords: ['работа', 'программист'],
    vk_url: 'https://vk.com/wall-98765_333?reply=444'
  },
  {
    id: 3,
    text: 'Куплю подержанный велосипед для ребенка',
    author_name: 'Игорь Иванов',
    author_id: 98765,
    group_name: 'Детские товары',
    group_id: 13579,
    post_id: 555,
    comment_id: 666,
    created_at: '2024-01-15T12:00:00Z',
    likes_count: 3,
    replies_count: 1,
    matched_keywords: ['куплю', 'велосипед'],
    vk_url: 'https://vk.com/wall-13579_555?reply=666'
  }
]

export default function CommentsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedKeyword, setSelectedKeyword] = useState('')
  const [selectedGroup, setSelectedGroup] = useState('')
  const [dateRange, setDateRange] = useState('all')
  const [isLoading, setIsLoading] = useState(false)

  // Фильтрация комментариев
  const filteredComments = mockComments.filter(comment => {
    const matchesSearch = comment.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         comment.author_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         comment.group_name.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesKeyword = !selectedKeyword || 
                          comment.matched_keywords.some(kw => kw.includes(selectedKeyword))
    
    const matchesGroup = !selectedGroup || comment.group_name === selectedGroup
    
    // Простая фильтрация по дате (в реальном приложении будет более сложная)
    const matchesDate = dateRange === 'all' || true
    
    return matchesSearch && matchesKeyword && matchesGroup && matchesDate
  })

  const totalComments = mockComments.length
  const todayComments = mockComments.filter(c => 
    new Date(c.created_at).toDateString() === new Date().toDateString()
  ).length

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('ru-RU').format(num)
  }

  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 60) return `${diffInMinutes} мин назад`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} ч назад`
    return `${Math.floor(diffInMinutes / 1440)} дн назад`
  }

  const getKeywordColor = (keyword: string) => {
    const colors = ['bg-blue-100 text-blue-800', 'bg-green-100 text-green-800', 'bg-purple-100 text-purple-800', 'bg-orange-100 text-orange-800']
    return colors[keyword.length % colors.length]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinnerWithText text="Загрузка комментариев..." size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Комментарии</h1>
          <p className="text-gray-600 mt-2">
            Поиск и анализ комментариев ВКонтакте с ключевыми словами
          </p>
        </div>
        <Button>
          <TrendingUp className="h-4 w-4 mr-2" />
          Экспорт данных
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Всего комментариев</p>
                <p className="text-2xl font-bold">{formatNumber(totalComments)}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Сегодня</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatNumber(todayComments)}
                </p>
              </div>
              <Calendar className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Найдено</p>
                <p className="text-2xl font-bold text-purple-600">
                  {formatNumber(filteredComments.length)}
                </p>
              </div>
              <Eye className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Активность</p>
                <p className="text-2xl font-bold text-orange-600">85%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по тексту, автору..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            {/* Keyword Filter */}
            <div>
              <input
                type="text"
                placeholder="Фильтр по ключевому слову"
                value={selectedKeyword}
                onChange={(e) => setSelectedKeyword(e.target.value)}
                className="px-3 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Group Filter */}
            <div>
              <select
                value={selectedGroup}
                onChange={(e) => setSelectedGroup(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Все группы</option>
                <option value="Барахолка СПб">Барахолка СПб</option>
                <option value="IT Вакансии Москва">IT Вакансии Москва</option>
                <option value="Детские товары">Детские товары</option>
              </select>
            </div>

            {/* Date Range */}
            <div>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Все время</option>
                <option value="today">Сегодня</option>
                <option value="week">Неделя</option>
                <option value="month">Месяц</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comments List */}
      <div className="space-y-4">
        {filteredComments.length > 0 ? (
          filteredComments.map((comment) => (
            <Card key={comment.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="space-y-4">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{comment.author_name}</h3>
                        <p className="text-sm text-gray-600">
                          в группе {comment.group_name} • {formatRelativeTime(comment.created_at)}
                        </p>
                      </div>
                    </div>
                    
                    <a
                      href={comment.vk_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>

                  {/* Comment Text */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-900">{comment.text}</p>
                  </div>

                  {/* Keywords */}
                  <div className="flex flex-wrap gap-2">
                    <span className="text-sm text-gray-600">Ключевые слова:</span>
                    {comment.matched_keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className={`px-2 py-1 rounded-full text-xs font-medium ${getKeywordColor(keyword)}`}
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>

                  {/* Stats */}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Heart className="h-4 w-4" />
                        <span>{comment.likes_count}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageCircle className="h-4 w-4" />
                        <span>{comment.replies_count}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className="text-xs">
                        ID: {comment.comment_id}
                      </Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="p-12">
              <div className="text-center">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Комментарии не найдены
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchTerm || selectedKeyword || selectedGroup
                    ? 'Измените критерии поиска или очистите фильтры'
                    : 'Запустите парсинг групп для получения комментариев'
                  }
                </p>
                <Button variant="outline">
                  <Filter className="h-4 w-4 mr-2" />
                  Сбросить фильтры
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Load More */}
      {filteredComments.length > 0 && (
        <div className="text-center">
          <Button variant="outline">
            Загрузить еще комментарии
          </Button>
        </div>
      )}
    </div>
  )
} 