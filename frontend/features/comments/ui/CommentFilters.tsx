'use client'

import { Search, X, Eye, EyeOff } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Label } from '@/shared/ui'

import { CommentFilters as CommentFiltersType } from '@/entities/comment'

interface CommentFiltersProps {
 filters: CommentFiltersType
 onFiltersChange: (filters: CommentFiltersType) => void
}

export function CommentFilters({ filters, onFiltersChange }: CommentFiltersProps) {
 const updateFilter = <K extends keyof CommentFiltersType>(
  key: K,
  value: CommentFiltersType[K]
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
       placeholder="Поиск комментариев по тексту..."
       className="pl-10"
      // Note: Text search would need backend implementation
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
   <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
    {/* Group ID Filter */}
    <div className="space-y-2">
     <Label htmlFor="groupId">ID группы</Label>
     <Input
      id="groupId"
      type="number"
      placeholder="Фильтр по ID группы VK..."
      value={filters.group_id?.toString() || ''}
      onChange={(e) => updateFilter('group_id', e.target.value ? parseInt(e.target.value) : undefined)}
     />
    </div>

    {/* Keyword ID Filter */}
    <div className="space-y-2">
     <Label htmlFor="keywordId">ID ключевого слова</Label>
     <Input
      id="keywordId"
      type="number"
      placeholder="Фильтр по ID ключевого слова..."
      value={filters.keyword_id?.toString() || ''}
      onChange={(e) => updateFilter('keyword_id', e.target.value ? parseInt(e.target.value) : undefined)}
     />
    </div>

    {/* Author Screen Name Filter */}
    <div className="space-y-2">
     <Label htmlFor="authorScreenName">Автор</Label>
     <Input
      id="authorScreenName"
      placeholder="Фильтр по screen name автора..."
     // Note: Author screen name filter would need backend implementation
     />
    </div>
   </div>

   {/* Status Toggles */}
   <div className="flex flex-wrap gap-6">
    <div className="flex items-center space-x-2">
     <Switch
      id="viewed-only"
      checked={filters.is_viewed === true}
      onCheckedChange={(checked) => updateFilter('is_viewed', checked || undefined)}
     />
     <Label htmlFor="viewed-only" className="text-sm flex items-center gap-1">
      <Eye className="h-4 w-4" />
      Показывать только просмотренные комментарии
     </Label>
    </div>

    <div className="flex items-center space-x-2">
     <Switch
      id="unviewed-only"
      checked={filters.is_viewed === false}
      onCheckedChange={(checked) => updateFilter('is_viewed', checked ? false : undefined)}
     />
     <Label htmlFor="unviewed-only" className="text-sm flex items-center gap-1">
      <EyeOff className="h-4 w-4" />
      Показывать только новые комментарии
     </Label>
    </div>
   </div>
  </div>
 )
}
