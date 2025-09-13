'use client'

import { Filter, X } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

interface MonitoringFiltersProps {
  filters: {
    types?: string[]
  }
  onFiltersChange: (filters: { types?: string[] }) => void
}

const EVENT_TYPES = [
  { value: 'success', label: 'Успешные', color: 'bg-green-500' },
  { value: 'warning', label: 'Предупреждения', color: 'bg-orange-500' },
  { value: 'error', label: 'Ошибки', color: 'bg-red-500' },
  { value: 'info', label: 'Информация', color: 'bg-blue-500' },
]

export function MonitoringFilters({ filters, onFiltersChange }: MonitoringFiltersProps) {
  const toggleFilter = (type: string) => {
    const currentTypes = filters.types || []
    const newTypes = currentTypes.includes(type)
      ? currentTypes.filter(t => t !== type)
      : [...currentTypes, type]

    const { types, ...restFilters } = filters
    if (newTypes.length > 0) {
      onFiltersChange({
        ...restFilters,
        types: newTypes,
      })
    } else {
      onFiltersChange(restFilters)
    }
  }

  const clearFilters = () => {
    onFiltersChange({})
  }

  const hasActiveFilters = filters.types && filters.types.length > 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Filter className="h-5 w-5" />
          Фильтры событий
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {EVENT_TYPES.map(type => (
            <Button
              key={type.value}
              variant={filters.types?.includes(type.value) ? 'default' : 'outline'}
              size="sm"
              onClick={() => toggleFilter(type.value)}
              className="gap-2"
            >
              <div className={`w-2 h-2 rounded-full ${type.color}`}></div>
              {type.label}
            </Button>
          ))}
        </div>

        {hasActiveFilters && (
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="flex flex-wrap gap-1">
              {filters.types?.map(type => {
                const typeInfo = EVENT_TYPES.find(t => t.value === type)
                return (
                  <Badge key={type} variant="secondary" className="gap-1">
                    <div className={`w-2 h-2 rounded-full ${typeInfo?.color}`}></div>
                    {typeInfo?.label}
                  </Badge>
                )
              })}
            </div>
            <Button variant="outline" size="sm" onClick={clearFilters}>
              <X className="mr-2 h-4 w-4" />
              Очистить
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
