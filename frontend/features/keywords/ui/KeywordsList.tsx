'use client'

import { Hash, MessageSquare, FolderOpen } from 'lucide-react'

import { Keyword } from '@/entities/keywords'
import { KeywordCard } from '@/features/keywords/ui/KeywordCard'
import type { KeywordFormData } from '@/features/keywords/ui/KeywordForm'

interface KeywordsListProps {
  keywords: Keyword[]
  loading?: boolean
  onUpdate?: (id: number, updates: KeywordFormData) => void
  onDelete?: (id: number) => void
  onToggleStatus?: (id: number, isActive: boolean) => void
}

export function KeywordsList({
  keywords,
  loading,
  onUpdate,
  onDelete,
  onToggleStatus,
}: KeywordsListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white border border-gray-200 rounded-lg">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="h-6 w-48 bg-gray-200 rounded animate-pulse" />
                <div className="h-8 w-8 bg-gray-200 rounded animate-pulse" />
              </div>
              <div className="space-y-2">
                <div className="h-4 w-full bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-3/4 bg-gray-200 rounded animate-pulse" />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (keywords.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="py-12 px-6">
          <div className="text-center space-y-4">
            <Hash className="mx-auto h-16 w-16 text-gray-400" />
            <div>
              <h3 className="text-lg font-medium">Ключевые слова не найдены</h3>
              <p className="text-gray-600">
                {loading
                  ? 'Загрузка ключевых слов...'
                  : 'Добавьте свое первое ключевое слово для начала мониторинга комментариев'}
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Всего ключевых слов</h3>
            <Hash className="h-4 w-4 text-gray-400" />
          </div>
          <div className="text-2xl font-bold">{keywords.length}</div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Активные ключевые слова</h3>
            <FolderOpen className="h-4 w-4 text-gray-400" />
          </div>
          <div className="text-2xl font-bold">
            {keywords.filter(k => k.status.is_active).length}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Всего совпадений</h3>
            <MessageSquare className="h-4 w-4 text-gray-400" />
          </div>
          <div className="text-2xl font-bold">
            {keywords.reduce((sum, keyword) => sum + (keyword.match_count ?? 0), 0).toLocaleString()}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Категории</h3>
            <FolderOpen className="h-4 w-4 text-gray-400" />
          </div>
          <div className="text-2xl font-bold">
            {new Set(keywords.map(k => k.category).filter(Boolean)).size}
          </div>
        </div>
      </div>

      {/* Keywords Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {keywords.map(keyword => (
          <KeywordCard
            key={keyword.id}
            keyword={keyword}
            onUpdate={onUpdate || (() => {})}
            onDelete={onDelete || (() => {})}
            onToggleStatus={onToggleStatus || (() => {})}
          />
        ))}
      </div>
    </div>
  )
}
