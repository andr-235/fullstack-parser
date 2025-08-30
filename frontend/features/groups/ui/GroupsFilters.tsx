'use client'

import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { GroupsFilters as GroupsFiltersType } from '@/entities/groups'
import { Search, X, Eye, EyeOff } from 'lucide-react'

interface GroupsFiltersProps {
 filters: GroupsFiltersType
 onFiltersChange: (filters: GroupsFiltersType) => void
}

export function GroupsFilters({ filters, onFiltersChange }: GroupsFiltersProps) {
 const updateFilter = <K extends keyof GroupsFiltersType>(
  key: K,
  value: GroupsFiltersType[K]
 ) => {
  onFiltersChange({
   ...filters,
   [key]: value,
  })
 }

 const clearFilters = () => {
  onFiltersChange({})
 }

 const hasActiveFilters = Object.values(filters).some(value =>
  value !== undefined && value !== null && value !== ''
 )

 return (
  <div className="space-y-4">
   {/* Search and Quick Actions */}
   <div className="flex items-center gap-4 flex-wrap">
    <div className="flex-1 min-w-[300px]">
     <div className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
      <Input
       placeholder="Поиск групп по названию или screen name..."
       className="pl-10"
       value={filters.search || ''}
       onChange={(e) => updateFilter('search', e.target.value || undefined)}
      />
     </div>
    </div>

    {hasActiveFilters && (
     <Button
      variant="outline"
      size="sm"
      onClick={clearFilters}
      className="shrink-0"
     >
      <X className="mr-2 h-4 w-4" />
      Очистить фильтры
     </Button>
    )}
   </div>

   {/* Status Toggles */}
   <div className="flex flex-wrap gap-6">
    <div className="flex items-center space-x-2">
     <Switch
      id="active-only"
      checked={filters.active_only !== false}
      onCheckedChange={(checked) => updateFilter('active_only', checked)}
     />
     <Label htmlFor="active-only" className="text-sm flex items-center gap-1">
      <Eye className="h-4 w-4" />
      Показывать только активные группы
     </Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch
      id="inactive-only"
      checked={filters.active_only === false}
      onCheckedChange={(checked) => updateFilter('active_only', checked ? false : undefined)}
     />
     <Label htmlFor="inactive-only" className="text-sm flex items-center gap-1">
      <EyeOff className="h-4 w-4" />
      Показывать только неактивные группы
     </Label>
    </div>
   </div>
  </div>
 )
}
