'use client'

import { Filter, X, Settings, Database, Bell, Palette, Globe } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

interface SettingsFiltersProps {
  filters: {
    categories?: string[]
    statuses?: string[]
  }
  onFiltersChange: (filters: { categories?: string[]; statuses?: string[] }) => void
}

const CATEGORIES = [
  { value: 'general', label: 'Общие', icon: Settings, color: 'bg-blue-500' },
  { value: 'api', label: 'API', icon: Globe, color: 'bg-green-500' },
  { value: 'database', label: 'База данных', icon: Database, color: 'bg-purple-500' },
  { value: 'notifications', label: 'Уведомления', icon: Bell, color: 'bg-orange-500' },
  { value: 'appearance', label: 'Внешний вид', icon: Palette, color: 'bg-pink-500' },
]

const STATUSES = [
  { value: 'active', label: 'Активные', color: 'bg-green-500' },
  { value: 'inactive', label: 'Неактивные', color: 'bg-gray-500' },
  { value: 'warning', label: 'Предупреждения', color: 'bg-orange-500' },
  { value: 'info', label: 'Информационные', color: 'bg-blue-500' },
]

export function SettingsFilters({ filters, onFiltersChange }: SettingsFiltersProps) {
  const toggleCategoryFilter = (category: string) => {
    const currentCategories = filters.categories || []
    const newCategories = currentCategories.includes(category)
      ? currentCategories.filter(c => c !== category)
      : [...currentCategories, category]

    const { categories, ...restFilters } = filters
    if (newCategories.length > 0) {
      onFiltersChange({
        ...restFilters,
        categories: newCategories,
      })
    } else {
      onFiltersChange(restFilters)
    }
  }

  const toggleStatusFilter = (status: string) => {
    const currentStatuses = filters.statuses || []
    const newStatuses = currentStatuses.includes(status)
      ? currentStatuses.filter(s => s !== status)
      : [...currentStatuses, status]

    const { statuses, ...restFilters } = filters
    if (newStatuses.length > 0) {
      onFiltersChange({
        ...restFilters,
        statuses: newStatuses,
      })
    } else {
      onFiltersChange(restFilters)
    }
  }

  const clearFilters = () => {
    onFiltersChange({})
  }

  const hasActiveFilters =
    (filters.categories?.length || 0) > 0 || (filters.statuses?.length || 0) > 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Filter className="h-5 w-5" />
          Фильтры настроек
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Category Filters */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Категории</h4>
          <div className="flex flex-wrap gap-2">
            {CATEGORIES.map(category => {
              const Icon = category.icon
              return (
                <Button
                  key={category.value}
                  variant={filters.categories?.includes(category.value) ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => toggleCategoryFilter(category.value)}
                  className="gap-2"
                >
                  <Icon className="h-4 w-4" />
                  {category.label}
                </Button>
              )
            })}
          </div>
        </div>

        {/* Status Filters */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Статус</h4>
          <div className="flex flex-wrap gap-2">
            {STATUSES.map(status => (
              <Button
                key={status.value}
                variant={filters.statuses?.includes(status.value) ? 'default' : 'outline'}
                size="sm"
                onClick={() => toggleStatusFilter(status.value)}
                className="gap-2"
              >
                <div className={`w-2 h-2 rounded-full ${status.color}`}></div>
                {status.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Active Filters */}
        {hasActiveFilters && (
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="flex flex-wrap gap-2">
              {filters.categories?.map(category => {
                const categoryInfo = CATEGORIES.find(c => c.value === category)
                return (
                  <Badge key={category} variant="secondary" className="gap-1">
                    <div className={`w-2 h-2 rounded-full ${categoryInfo?.color}`}></div>
                    {categoryInfo?.label}
                  </Badge>
                )
              })}
              {filters.statuses?.map(status => {
                const statusInfo = STATUSES.find(s => s.value === status)
                return (
                  <Badge key={status} variant="secondary" className="gap-1">
                    <div className={`w-2 h-2 rounded-full ${statusInfo?.color}`}></div>
                    {statusInfo?.label}
                  </Badge>
                )
              })}
            </div>
            <Button variant="outline" size="sm" onClick={clearFilters} className="gap-2">
              <X className="h-4 w-4" />
              Очистить фильтры
            </Button>
          </div>
        )}

        {/* Filter Summary */}
        {hasActiveFilters && (
          <div className="text-sm text-muted-foreground">
            Найдено настроек: {(filters.categories?.length || 0) + (filters.statuses?.length || 0)}{' '}
            фильтр(ов)
          </div>
        )}
      </CardContent>
    </Card>
  )
}
