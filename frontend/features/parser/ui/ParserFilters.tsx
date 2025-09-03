'use client'

import { Filter, X } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Badge } from '@/shared/ui'

interface ParserFiltersProps {
 filters: {
  statuses?: string[]
 }
 onFiltersChange: (filters: { statuses?: string[] }) => void
}

const SESSION_STATUSES = [
 { value: 'completed', label: 'Завершенные', color: 'bg-green-500' },
 { value: 'partial', label: 'Частичные', color: 'bg-orange-500' },
 { value: 'failed', label: 'Ошибки', color: 'bg-red-500' },
]

export function ParserFilters({ filters, onFiltersChange }: ParserFiltersProps) {
 const toggleFilter = (status: string) => {
  const currentStatuses = filters.statuses || []
  const newStatuses = currentStatuses.includes(status)
   ? currentStatuses.filter(s => s !== status)
   : [...currentStatuses, status]

  const { statuses, ...restFilters } = filters
  if (newStatuses.length > 0) {
   onFiltersChange({
    ...restFilters,
    statuses: newStatuses
   })
  } else {
   onFiltersChange(restFilters)
  }
 }

 const clearFilters = () => {
  onFiltersChange({})
 }

 const hasActiveFilters = filters.statuses && filters.statuses.length > 0

 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2 text-lg">
     <Filter className="h-5 w-5" />
     Фильтры сессий
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    <div className="flex flex-wrap gap-2">
     {SESSION_STATUSES.map((status) => (
      <Button
       key={status.value}
       variant={filters.statuses?.includes(status.value) ? 'default' : 'outline'}
       size="sm"
       onClick={() => toggleFilter(status.value)}
       className="gap-2"
      >
       <div className={`w-2 h-2 rounded-full ${status.color}`}></div>
       {status.label}
      </Button>
     ))}
    </div>

    {hasActiveFilters && (
     <div className="flex items-center justify-between pt-2 border-t">
      <div className="flex flex-wrap gap-1">
       {filters.statuses?.map((status) => {
        const statusInfo = SESSION_STATUSES.find(s => s.value === status)
        return (
         <Badge key={status} variant="secondary" className="gap-1">
          <div className={`w-2 h-2 rounded-full ${statusInfo?.color}`}></div>
          {statusInfo?.label}
         </Badge>
        )
       })}
      </div>
      <Button
       variant="outline"
       size="sm"
       onClick={clearFilters}
      >
       <X className="mr-2 h-4 w-4" />
       Очистить
      </Button>
     </div>
    )}
   </CardContent>
  </Card>
 )
}
