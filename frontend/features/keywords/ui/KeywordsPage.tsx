'use client'

import { useState, useEffect } from 'react'

import { Plus, RefreshCw } from 'lucide-react'

import { Button } from '@/shared/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/shared/ui'
import { FileUploadModal } from '@/shared/ui'
import { Alert, AlertDescription } from '@/shared/ui'

import {
  KeywordsFilters as KeywordsFiltersType,
  CreateKeywordRequest,
  UpdateKeywordRequest,
} from '@/entities/keywords'
import { useKeywords } from '@/entities/keywords'

import { KeywordForm } from '@/features/keywords/ui/KeywordForm'
import { KeywordsFilters } from '@/features/keywords/ui/KeywordsFilters'
import { KeywordsList } from '@/features/keywords/ui/KeywordsList'

const FILTERS_STORAGE_KEY = 'keywords-filters'

export function KeywordsPage() {
  const [filters, setFilters] = useState<KeywordsFiltersType>({
    active_only: true,
  })
  const [showCreateForm, setShowCreateForm] = useState(false)

  // Загружаем фильтры из localStorage при инициализации
  useEffect(() => {
    const savedFilters = localStorage.getItem(FILTERS_STORAGE_KEY)
    if (savedFilters) {
      try {
        const parsedFilters = JSON.parse(savedFilters)
        setFilters(parsedFilters)
      } catch (error) {
        // Игнорируем ошибки парсинга, используем значения по умолчанию
      }
    }
  }, [])

  // Сохраняем фильтры в localStorage при изменении
  useEffect(() => {
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(filters))
  }, [filters])

  const {
    keywords,
    loading,
    error,
    createKeyword,
    updateKeyword,
    deleteKeyword,
    toggleKeywordStatus,
    refetch,
  } = useKeywords(filters)

  const handleCreateKeyword = async (data: {
    word: string
    category?: string | undefined
    description?: string | undefined
    is_active?: boolean | undefined
    is_case_sensitive?: boolean | undefined
    is_whole_word?: boolean | undefined
  }) => {
    try {
      // Преобразуем данные формы в формат API
      const createData: CreateKeywordRequest = {
        word: data.word,
        ...(data.category && { category_name: data.category }),
        ...(data.description && { description: data.description }),
        priority: 0, // Значение по умолчанию
      }
      await createKeyword(createData)
      setShowCreateForm(false)
      refetch()
    } catch (err) {
      throw err
    }
  }

  const handleUpdateKeyword = async (id: number, updates: UpdateKeywordRequest) => {
    try {
      await updateKeyword(id, updates)
      refetch()
    } catch (err) {
      throw err
    }
  }

  const handleDeleteKeyword = async (id: number) => {
    try {
      await deleteKeyword(id)
      refetch()
    } catch (err) {
      throw err
    }
  }

  const handleToggleStatus = async (id: number, isActive: boolean) => {
    try {
      await toggleKeywordStatus(id, isActive)
      refetch()
    } catch (err) {
      throw err
    }
  }

  const handleFiltersChange = (newFilters: KeywordsFiltersType) => {
    setFilters(newFilters)
  }

  const handleRefresh = () => {
    refetch()
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ключевые слова</h1>
          <p className="text-muted-foreground">
            Управление ключевыми словами для мониторинга и фильтрации комментариев
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Обновить
          </Button>

          <FileUploadModal
            type="keywords"
            triggerText="Загрузить из файла"
            onSuccess={handleRefresh}
            apiParams={{
              is_active: true,
              is_case_sensitive: false,
              is_whole_word: false,
            }}
          />

          <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Добавить ключевое слово
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Добавить новое ключевое слово</DialogTitle>
              </DialogHeader>
              <KeywordForm
                onSubmit={handleCreateKeyword}
                onCancel={() => setShowCreateForm(false)}
              />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Фильтры</CardTitle>
        </CardHeader>
        <CardContent>
          <KeywordsFilters filters={filters} onFiltersChange={handleFiltersChange} />
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Alert className="border-destructive">
          <AlertDescription>
            Ошибка загрузки ключевых слов: {error}
            <Button variant="outline" size="sm" onClick={handleRefresh} className="ml-4">
              Попробовать снова
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Keywords List */}
      <KeywordsList
        keywords={keywords}
        loading={loading}
        onUpdate={handleUpdateKeyword}
        onDelete={handleDeleteKeyword}
        onToggleStatus={handleToggleStatus}
      />
    </div>
  )
}
