'use client'

import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { KeywordsFilters as KeywordsFiltersType, KEYWORD_CATEGORIES } from '@/entities/keywords'
import { Search, X, Eye, EyeOff } from 'lucide-react'

interface KeywordsFiltersProps {
 filters: KeywordsFiltersType
 onFiltersChange: (filters: KeywordsFiltersType) => void
}

export function KeywordsFilters({ filters, onFiltersChange }: KeywordsFiltersProps) {
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
       placeholder="Поиск ключевых слов по слову..."
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

   {/* Filter Controls */}
   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    {/* Category Filter */}
    <div className="space-y-2">
     <Label htmlFor="category">Категория</Label>
     <Select
      value={filters.category || 'all'}
      onValueChange={(value) => updateFilter('category', value === 'all' ? undefined : value)}
     >
      <SelectTrigger>
       <SelectValue placeholder="Выберите категорию" />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="all">Все категории</SelectItem>
       {KEYWORD_CATEGORIES.map((category) => (
        <SelectItem key={category.key} value={category.key}>
         {category.label}
        </SelectItem>
       ))}
      </SelectContent>
     </Select>
    </div>

    {/* Empty placeholder for future filters */}
    <div className="space-y-2">
     <Label>Дополнительные фильтры</Label>
     <p className="text-sm text-muted-foreground">
      Здесь будут доступны дополнительные опции фильтрации
     </p>
    </div>
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
      Показывать только активные ключевые слова
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
      Показывать только неактивные ключевые слова
     </Label>
    </div>
   </div>
  </div>
 )
}
