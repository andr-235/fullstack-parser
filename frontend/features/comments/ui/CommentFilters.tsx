'use client'

import { Search, X, Eye, EyeOff } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Label } from '@/shared/ui'

import { CommentFilter } from '@/features/comments'

interface CommentFiltersProps {
  filters: CommentFilter
  onFiltersChange: (filters: CommentFilter) => void
}

export function CommentFilters({ filters, onFiltersChange }: CommentFiltersProps) {
  const updateFilter = <K extends keyof CommentFilter>(
    key: K,
    value: CommentFilter[K]
  ) => {
    onFiltersChange({
      ...filters,
      [key]: value,
    })
  }

  const clearFilters = () => {
    onFiltersChange({
      search_text: '',
      is_deleted: false,
    })
  }

  const hasActiveFilters = Object.values(filters).some(
    value => value !== undefined && value !== null && value !== ''
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
              value={filters.search_text || ''}
              onChange={e => updateFilter('search_text', e.target.value || undefined)}
            />
          </div>
        </div>

        {hasActiveFilters && (
          <Button variant="outline" size="sm" onClick={clearFilters} className="shrink-0">
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
            onChange={e =>
              updateFilter('group_id', e.target.value ? parseInt(e.target.value) : undefined)
            }
          />
        </div>

        {/* Post ID Filter */}
        <div className="space-y-2">
          <Label htmlFor="postId">ID поста</Label>
          <Input
            id="postId"
            type="number"
            placeholder="Фильтр по ID поста..."
            value={filters.post_id?.toString() || ''}
            onChange={e =>
              updateFilter('post_id', e.target.value ? parseInt(e.target.value) : undefined)
            }
          />
        </div>

        {/* Author ID Filter */}
        <div className="space-y-2">
          <Label htmlFor="authorId">ID автора</Label>
          <Input
            id="authorId"
            type="number"
            placeholder="Фильтр по ID автора..."
            value={filters.author_id?.toString() || ''}
            onChange={e =>
              updateFilter('author_id', e.target.value ? parseInt(e.target.value) : undefined)
            }
          />
        </div>
      </div>

      {/* Status Toggles */}
      <div className="flex flex-wrap gap-6">
        <div className="flex items-center space-x-2">
          <Switch
            id="deleted-only"
            checked={filters.is_deleted === true}
            onCheckedChange={checked => updateFilter('is_deleted', checked || false)}
          />
          <Label htmlFor="deleted-only" className="text-sm flex items-center gap-1">
            <EyeOff className="h-4 w-4" />
            Показывать только удаленные комментарии
          </Label>
        </div>
      </div>
    </div>
  )
}
