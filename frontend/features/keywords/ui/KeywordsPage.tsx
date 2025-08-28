'use client'

import React, { useState } from 'react'
import {
  useKeywords,
  useCreateKeyword,
  useUpdateKeyword,
  useDeleteKeyword,
  useInfiniteKeywords,
  useUpdateKeywordsStats,
  useTotalMatches,
} from '@/entities/keyword'
import {
  PageHeader,
  StatsGrid,
  StatsCard,
  DataTable,
  LoadingState,
  EmptyState,
  ErrorState,
  SearchInput,
  FilterPanel,
  useSearch,
  useFilters,
  PageContainer,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/shared/ui'

import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import { LoadingSpinner } from '@/shared/ui'
import {
  Plus,
  Trash2,
  Search,
  Check,
  X,
  Hash,
  Target,
  MessageSquare,
  Activity,
} from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { KeywordResponse, KeywordUpdate } from '@/shared/types'
import { useDebounce } from '@/shared/hooks'
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from '@/shared/ui'
import { Label } from '@/shared/ui'
import { useKeywordCategories } from '@/entities/keyword'
import { cn } from '@/shared/lib/utils'
import UploadKeywordsModal from './UploadKeywordsModal'



export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [newKeyword, setNewKeyword] = useState('')
  const [newKeywordCategory, setNewKeywordCategory] = useState('')
  const [activeOnly, setActiveOnly] = useState(true)
  const [category, setCategory] = useState<string>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(1000) // Увеличиваем лимит для загрузки большего количества записей

  // Конфигурация колонок для DataTable
  const columns = [
    {
      key: 'word' as keyof KeywordResponse,
      title: 'Ключевое слово',
      sortable: true,
      width: '300px',
      render: (value: string, record: KeywordResponse) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <Hash className="h-4 w-4 text-white" />
          </div>
          <span className="font-medium text-foreground cursor-pointer hover:text-primary transition-colors">
            {value}
          </span>
        </div>
      ),
    },
    {
      key: 'category' as keyof KeywordResponse,
      title: 'Категория',
      render: (value: string) => (
        <span className="text-muted-foreground text-sm">
          {value || '—'}
        </span>
      ),
    },
    {
      key: 'total_matches' as keyof KeywordResponse,
      title: 'Найдено',
      sortable: true,
      render: (value: number) => (
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-primary" />
          <span className="font-semibold text-primary">
            {value}
          </span>
        </div>
      ),
    },
    {
      key: 'is_active' as keyof KeywordResponse,
      title: 'Статус',
      render: (value: boolean) => (
        <Badge
          variant={value ? 'default' : 'secondary'}
        >
          {value ? 'Активно' : 'Неактивно'}
        </Badge>
      ),
    },
    {
      key: 'actions' as keyof KeywordResponse,
      title: 'Действия',
      render: (value: any, record: KeywordResponse) => (
        <Button
          variant="ghost"
          size="icon"
          onClick={() => handleDeleteKeyword(record.id)}
          disabled={deleteKeywordMutation.isPending}
          className="hover:bg-destructive/10 text-destructive hover:text-destructive transition-all duration-200 hover:scale-110"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      ),
    },
  ]

  // Пагинация
  const { data, isLoading, error, refetch } = useKeywords({
    q: searchTerm,
    active_only: activeOnly,
    category: category || undefined,
    page: currentPage,
    size: itemsPerPage,
  })

  const keywords = data?.items || []
  const total = data?.total || 0
  const active = keywords.filter((k: any) => k.is_active).length || 0

  // Получаем общее количество совпадений
  const { data: totalMatchesData } = useTotalMatches()
  const totalMatches = totalMatchesData?.total_matches || 0

  // Сброс страницы при изменении фильтров
  React.useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, activeOnly, category])

  const totalPages = Math.ceil(total / itemsPerPage)

  const { data: categoriesData } = useKeywordCategories()
  const createKeywordMutation = useCreateKeyword()
  const updateKeywordMutation = useUpdateKeyword()
  const deleteKeywordMutation = useDeleteKeyword()
  const updateStatsMutation = useUpdateKeywordsStats()

  // Автоматически обновляем статистику при загрузке страницы
  React.useEffect(() => {
    updateStatsMutation.mutate()
  }, [])

  const handleAddKeyword = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newKeyword.trim()) return
    createKeywordMutation.mutate(
      {
        word: newKeyword,
        is_active: true,
        is_case_sensitive: false,
        is_whole_word: false,
        category: newKeywordCategory.trim() || '',
      },
      {
        onSuccess: () => {
          setNewKeyword('')
          setNewKeywordCategory('')
          toast.success('Ключевое слово добавлено! 🎯')
        },
      }
    )
  }

  const handleDeleteKeyword = (id: number) => {
    if (window.confirm('Удалить ключевое слово?')) {
      deleteKeywordMutation.mutate(id, {
        onSuccess: () => toast.success('Ключевое слово удалено! 🗑️'),
      })
    }
  }

  const handleUpdateKeyword = (
    id: number,
    data: KeywordUpdate,
    callbacks?: { onSuccess?: () => void; onError?: () => void }
  ) => {
    if (callbacks) {
      updateKeywordMutation.mutate({ keywordId: id, data }, callbacks)
    } else {
      updateKeywordMutation.mutateAsync({ keywordId: id, data })
    }
  }

  return (
    <PageContainer background="gradient">
      {/* Заголовок */}
      <PageHeader
        title="Управление ключевыми словами"
        description="Добавляйте, настраивайте и управляйте ключевыми словами для поиска в комментариях"
        icon={Target}
      />

      {/* Статистика */}
      <StatsGrid
        stats={[
          {
            title: "Всего слов",
            value: total,
            icon: Hash,
            color: "purple"
          },
          {
            title: "Активных",
            value: active,
            icon: Activity,
            color: "green"
          },
          {
            title: "Найдено",
            value: totalMatches,
            icon: MessageSquare,
            color: "blue"
          }
        ]}
      />

      {/* Управление */}
      <Card className="border-border bg-card shadow-lg">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold text-card-foreground">
            Управление ключевыми словами
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Поиск и фильтры */}
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1">
              <SearchInput
                value={searchTerm}
                onChange={setSearchTerm}
                placeholder="Поиск по ключевым словам..."
              />
            </div>

            <div className="flex items-center space-x-4">
              <label className="flex items-center space-x-2 text-sm text-muted-foreground">
                <Switch
                  checked={activeOnly}
                  onCheckedChange={setActiveOnly}
                  className="data-[state=checked]:bg-primary"
                />
                <span>Только активные</span>
              </label>

              <Select
                value={category || 'all'}
                onValueChange={(v) => setCategory(v === 'all' ? '' : v)}
              >
                <SelectTrigger className="w-40 border-input bg-background text-foreground">
                  <SelectValue placeholder="Все категории" />
                </SelectTrigger>
                <SelectContent className="bg-popover border-border">
                  <SelectItem
                    value="all"
                    className="text-popover-foreground hover:bg-accent"
                  >
                    Все категории
                  </SelectItem>
                  {(categoriesData || []).map((cat: string) => (
                    <SelectItem
                      key={cat}
                      value={cat}
                      className="text-popover-foreground hover:bg-accent"
                    >
                      {cat}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <UploadKeywordsModal onSuccess={() => refetch()} />
            </div>
          </div>

          {/* Форма добавления */}
          <form onSubmit={handleAddKeyword} className="flex gap-2">
            <Input
              placeholder="Новое ключевое слово"
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              disabled={createKeywordMutation.isPending}
              className="flex-1"
            />
            <Input
              placeholder="Категория (необязательно)"
              value={newKeywordCategory}
              onChange={(e) => setNewKeywordCategory(e.target.value)}
              disabled={createKeywordMutation.isPending}
              className="w-40"
            />
            <Button
              type="submit"
              disabled={createKeywordMutation.isPending}
              className="px-6 transition-all duration-200 hover:scale-105"
            >
              {createKeywordMutation.isPending ? (
                <LoadingSpinner className="h-4 w-4" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              <span className="ml-2">Добавить</span>
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Таблица ключевых слов */}
      {error ? (
        <ErrorState
          title="Ошибка загрузки"
          message={(error as Error)?.message || 'Не удалось загрузить ключевые слова'}
          fullHeight={false}
        />
      ) : (
        <DataTable
          data={keywords}
          columns={columns}
          loading={isLoading}
          emptyText="Нет ключевых слов"
          sortConfig={{
            key: 'total_matches' as keyof KeywordResponse,
            direction: 'desc',
            onSort: (key, direction) => {
              // Можно добавить сортировку здесь если нужно
              console.log('Sort by:', key, direction)
            },
          }}
        />
      )}
    </PageContainer>
  )
}
