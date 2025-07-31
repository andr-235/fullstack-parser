'use client'

import React from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui'
import { Button } from '@/shared/ui'
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react'

export type SortField =
  | 'published_at'
  | 'author_name'
  | 'likes_count'
  | 'matched_keywords_count'
  | 'created_at'
export type SortOrder = 'asc' | 'desc'

interface CommentsSortingProps {
  sortField: SortField
  sortOrder: SortOrder
  onSortChange: (field: SortField, order: SortOrder) => void
}

const sortOptions = [
  { value: 'published_at', label: 'Дата публикации' },
  { value: 'author_name', label: 'Автор' },
  { value: 'likes_count', label: 'Лайки' },
  { value: 'matched_keywords_count', label: 'Ключевые слова' },
  { value: 'created_at', label: 'Дата добавления' },
]

export function CommentsSorting({
  sortField,
  sortOrder,
  onSortChange,
}: CommentsSortingProps) {
  const handleFieldChange = (field: string) => {
    onSortChange(field as SortField, sortOrder)
  }

  const handleOrderToggle = () => {
    const newOrder = sortOrder === 'asc' ? 'desc' : 'asc'
    onSortChange(sortField, newOrder)
  }

  const getOrderIcon = () => {
    if (sortOrder === 'asc') {
      return <ArrowUp className="w-4 h-4" />
    }
    return <ArrowDown className="w-4 h-4" />
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-slate-400">Сортировка:</span>

      <Select value={sortField} onValueChange={handleFieldChange}>
        <SelectTrigger className="w-48">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {sortOptions.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        onClick={handleOrderToggle}
        variant="outline"
        size="sm"
        className="flex items-center gap-1"
      >
        {getOrderIcon()}
        {sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'}
      </Button>
    </div>
  )
}
