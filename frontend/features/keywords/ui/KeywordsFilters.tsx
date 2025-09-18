'use client'

import { Search, X, Eye, EyeOff } from 'lucide-react'

import { KeywordsFilters as KeywordsFiltersType, KEYWORD_CATEGORIES } from '@/entities/keywords'

interface KeywordsFiltersProps {
  filters: KeywordsFiltersType
  onFiltersChange: (filters: KeywordsFiltersType) => void
  disabled?: boolean
}

export function KeywordsFilters({ filters, onFiltersChange, disabled = false }: KeywordsFiltersProps) {
  const updateFilter = <K extends keyof KeywordsFiltersType>(
    key: K,
    value: KeywordsFiltersType[K]
  ) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    })
  }

  const clearFilters = () => {
    onFiltersChange({
      active_only: true, // Сохраняем базовый фильтр
    })
  }

  const hasActiveFilters = Object.entries(filters).some(([key, value]) => {
    // Не считаем active_only: true как активный фильтр, так как это базовое состояние
    if (key === 'active_only' && value === true) return false
    return value !== undefined && value !== null && value !== ''
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex-1 min-w-[300px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Поиск ключевых слов по слову..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              value={filters.search || ''}
              onChange={e => updateFilter('search', e.target.value || undefined)}
              disabled={disabled}
            />
          </div>
        </div>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-2 shrink-0 disabled:bg-gray-100 disabled:cursor-not-allowed"
            disabled={disabled}
          >
            <X className="h-4 w-4" />
            Очистить фильтры
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <label htmlFor="category" className="block text-sm font-medium text-gray-700">Категория</label>
          <select
            id="category"
            value={filters.category || 'all'}
            onChange={e => updateFilter('category', e.target.value === 'all' ? undefined : e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            disabled={disabled}
          >
            <option value="all">Все категории</option>
            {KEYWORD_CATEGORIES.map((category: { value: string; label: string }) => (
              <option key={category.value} value={category.value}>
                {category.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Дополнительные фильтры</label>
          <p className="text-sm text-gray-500">
            Здесь будут доступны дополнительные опции фильтрации
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-6">
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="active-only"
            checked={filters.active_only !== false}
            onChange={e => updateFilter('active_only', e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:cursor-not-allowed"
            disabled={disabled}
          />
          <label htmlFor="active-only" className="text-sm flex items-center gap-1 text-gray-700">
            <Eye className="h-4 w-4" />
            Показывать только активные ключевые слова
          </label>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="inactive-only"
            checked={filters.active_only === false}
            onChange={e => updateFilter('active_only', e.target.checked ? false : undefined)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:cursor-not-allowed"
            disabled={disabled}
          />
          <label htmlFor="inactive-only" className="text-sm flex items-center gap-1 text-gray-700">
            <EyeOff className="h-4 w-4" />
            Показывать только неактивные ключевые слова
          </label>
        </div>
      </div>
    </div>
  )
}
