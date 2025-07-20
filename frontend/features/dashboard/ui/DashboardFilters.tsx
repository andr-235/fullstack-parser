'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { 
  Search, 
  Filter, 
  Calendar, 
  Users, 
  Target, 
  X,
  RefreshCw
} from 'lucide-react'

/**
 * Интерфейс для фильтров дашборда
 */
export interface DashboardFilters {
  search: string
  dateRange: string
  groupId: number | null
  keywordId: number | null
  status: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

/**
 * Пропсы для компонента фильтров
 */
interface DashboardFiltersProps {
  filters: DashboardFilters
  onFiltersChange: (filters: DashboardFilters) => void
  onReset: () => void
  groups: Array<{ id: number; name: string }>
  keywords: Array<{ id: number; word: string }>
}

/**
 * Компонент фильтров для дашборда
 */
export function DashboardFilters({ 
  filters, 
  onFiltersChange, 
  onReset, 
  groups, 
  keywords 
}: DashboardFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const handleFilterChange = (key: keyof DashboardFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [key]: value
    })
  }

  const clearFilter = (key: keyof DashboardFilters) => {
    const newFilters = { ...filters }
    if (key === 'groupId' || key === 'keywordId') {
      newFilters[key] = null
    } else if (key === 'sortOrder') {
      newFilters[key] = 'desc'
    } else {
      newFilters[key] = ''
    }
    onFiltersChange(newFilters)
  }

  const hasActiveFilters = Object.values(filters).some(value => 
    value !== '' && value !== null && value !== 'all'
  )

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Фильтры
          </CardTitle>
          <div className="flex gap-2">
            {hasActiveFilters && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={onReset}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Сбросить
              </Button>
            )}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Скрыть' : 'Показать'}
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Поиск */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Поиск по комментариям, группам, ключевым словам..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Активные фильтры */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2">
            {filters.search && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Поиск: {filters.search}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => clearFilter('search')}
                />
              </Badge>
            )}
            {filters.dateRange && filters.dateRange !== 'all' && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Период: {filters.dateRange}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => clearFilter('dateRange')}
                />
              </Badge>
            )}
            {filters.groupId && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Группа: {groups.find(g => g.id === filters.groupId)?.name}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => clearFilter('groupId')}
                />
              </Badge>
            )}
            {filters.keywordId && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Ключевое слово: {keywords.find(k => k.id === filters.keywordId)?.word}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => clearFilter('keywordId')}
                />
              </Badge>
            )}
            {filters.status && filters.status !== 'all' && (
              <Badge variant="secondary" className="flex items-center gap-1">
                Статус: {filters.status}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => clearFilter('status')}
                />
              </Badge>
            )}
          </div>
        )}

        {/* Расширенные фильтры */}
        {isExpanded && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Период */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Период
              </label>
              <Select 
                value={filters.dateRange} 
                onValueChange={(value) => handleFilterChange('dateRange', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите период" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все время</SelectItem>
                  <SelectItem value="today">Сегодня</SelectItem>
                  <SelectItem value="yesterday">Вчера</SelectItem>
                  <SelectItem value="week">За неделю</SelectItem>
                  <SelectItem value="month">За месяц</SelectItem>
                  <SelectItem value="custom">Произвольный</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Группа */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <Users className="h-4 w-4" />
                Группа
              </label>
              <Select 
                value={filters.groupId?.toString() || 'all'} 
                onValueChange={(value) => handleFilterChange('groupId', value === 'all' ? null : parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите группу" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все группы</SelectItem>
                  {groups.map((group) => (
                    <SelectItem key={group.id} value={group.id.toString()}>
                      {group.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Ключевое слово */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                <Target className="h-4 w-4" />
                Ключевое слово
              </label>
              <Select 
                value={filters.keywordId?.toString() || 'all'} 
                onValueChange={(value) => handleFilterChange('keywordId', value === 'all' ? null : parseInt(value))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите ключевое слово" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все ключевые слова</SelectItem>
                  {keywords.map((keyword) => (
                    <SelectItem key={keyword.id} value={keyword.id.toString()}>
                      {keyword.word}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Статус */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Статус</label>
              <Select 
                value={filters.status} 
                onValueChange={(value) => handleFilterChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите статус" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Все статусы</SelectItem>
                  <SelectItem value="processed">Обработано</SelectItem>
                  <SelectItem value="unprocessed">Не обработано</SelectItem>
                  <SelectItem value="error">Ошибка</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Сортировка */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Сортировка</label>
              <Select 
                value={filters.sortBy} 
                onValueChange={(value) => handleFilterChange('sortBy', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Выберите сортировку" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">По дате</SelectItem>
                  <SelectItem value="likes">По лайкам</SelectItem>
                  <SelectItem value="matches">По совпадениям</SelectItem>
                  <SelectItem value="group">По группе</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Порядок сортировки */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Порядок</label>
              <Select 
                value={filters.sortOrder} 
                onValueChange={(value) => handleFilterChange('sortOrder', value as 'asc' | 'desc')}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="desc">По убыванию</SelectItem>
                  <SelectItem value="asc">По возрастанию</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Хук для управления фильтрами
 */
export function useDashboardFilters() {
  const [filters, setFilters] = useState<DashboardFilters>({
    search: '',
    dateRange: 'all',
    groupId: null,
    keywordId: null,
    status: 'all',
    sortBy: 'date',
    sortOrder: 'desc'
  })

  const resetFilters = () => {
    setFilters({
      search: '',
      dateRange: 'all',
      groupId: null,
      keywordId: null,
      status: 'all',
      sortBy: 'date',
      sortOrder: 'desc'
    })
  }

  return {
    filters,
    setFilters,
    resetFilters
  }
} 