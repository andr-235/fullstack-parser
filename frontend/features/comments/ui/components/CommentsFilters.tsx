'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Search, Filter, XCircle } from 'lucide-react'
import { useDebounce } from '@/shared/hooks'
import type { VKGroupResponse, KeywordResponse } from '@/types/api'

interface CommentsFiltersProps {
 groups: VKGroupResponse[]
 keywords: KeywordResponse[]
 filters: {
  text: string
  groupId: number | null
  keywordId: number | null
  authorScreenName: string[]
  dateFrom: string
  dateTo: string
  status: string
 }
 onFiltersChange: (filters: any) => void
 onReset: () => void
}

export function CommentsFilters({
 groups,
 keywords,
 filters,
 onFiltersChange,
 onReset,
}: CommentsFiltersProps) {
 const debouncedText = useDebounce(filters.text, 500)

 React.useEffect(() => {
  onFiltersChange({ ...filters, text: debouncedText })
 }, [debouncedText])

 const handleFilterChange = (key: string, value: any) => {
  onFiltersChange({ ...filters, [key]: value })
 }

 const handleAddSpecialAuthor = (authorScreenName: string) => {
  if (!filters.authorScreenName.includes(authorScreenName)) {
   handleFilterChange('authorScreenName', [...filters.authorScreenName, authorScreenName])
  }
 }

 const handleRemoveSpecialAuthor = (authorScreenName: string) => {
  handleFilterChange(
   'authorScreenName',
   filters.authorScreenName.filter((name) => name !== authorScreenName)
  )
 }

 return (
  <Card>
   <CardHeader>
    <CardTitle className="flex items-center gap-2">
     <Filter className="h-5 w-5" />
     Фильтры
    </CardTitle>
   </CardHeader>
   <CardContent className="space-y-4">
    {/* Поиск по тексту */}
    <div className="space-y-2">
     <label className="text-sm font-medium">Поиск по тексту</label>
     <div className="relative">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
      <Input
       placeholder="Введите текст для поиска..."
       value={filters.text}
       onChange={(e) => handleFilterChange('text', e.target.value)}
       className="pl-10"
      />
     </div>
    </div>

    {/* Фильтр по группе */}
    <div className="space-y-2">
     <label className="text-sm font-medium">Группа</label>
     <Select
      value={filters.groupId?.toString() || ''}
      onValueChange={(value) => handleFilterChange('groupId', value ? parseInt(value) : null)}
     >
      <SelectTrigger>
       <SelectValue placeholder="Все группы" />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="">Все группы</SelectItem>
       {groups.map((group) => (
        <SelectItem key={group.id} value={group.id.toString()}>
         {group.name}
        </SelectItem>
       ))}
      </SelectContent>
     </Select>
    </div>

    {/* Фильтр по ключевому слову */}
    <div className="space-y-2">
     <label className="text-sm font-medium">Ключевое слово</label>
     <Select
      value={filters.keywordId?.toString() || ''}
      onValueChange={(value) => handleFilterChange('keywordId', value ? parseInt(value) : null)}
     >
      <SelectTrigger>
       <SelectValue placeholder="Все ключевые слова" />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="">Все ключевые слова</SelectItem>
       {keywords.map((keyword) => (
        <SelectItem key={keyword.id} value={keyword.id.toString()}>
         {keyword.word}
        </SelectItem>
       ))}
      </SelectContent>
     </Select>
    </div>

    {/* Фильтр по статусу */}
    <div className="space-y-2">
     <label className="text-sm font-medium">Статус</label>
     <Select
      value={filters.status}
      onValueChange={(value) => handleFilterChange('status', value)}
     >
      <SelectTrigger>
       <SelectValue placeholder="Все статусы" />
      </SelectTrigger>
      <SelectContent>
       <SelectItem value="">Все статусы</SelectItem>
       <SelectItem value="new">Новые</SelectItem>
       <SelectItem value="viewed">Просмотренные</SelectItem>
       <SelectItem value="archived">Архивные</SelectItem>
      </SelectContent>
     </Select>
    </div>

    {/* Фильтр по дате */}
    <div className="grid grid-cols-2 gap-4">
     <div className="space-y-2">
      <label className="text-sm font-medium">Дата с</label>
      <Input
       type="date"
       value={filters.dateFrom}
       onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
      />
     </div>
     <div className="space-y-2">
      <label className="text-sm font-medium">Дата по</label>
      <Input
       type="date"
       value={filters.dateTo}
       onChange={(e) => handleFilterChange('dateTo', e.target.value)}
      />
     </div>
    </div>

    {/* Специальные авторы */}
    {filters.authorScreenName.length > 0 && (
     <div className="space-y-2">
      <label className="text-sm font-medium">Специальные авторы</label>
      <div className="flex flex-wrap gap-2">
       {filters.authorScreenName.map((author) => (
        <div
         key={author}
         className="flex items-center gap-1 bg-slate-700 px-2 py-1 rounded text-sm"
        >
         <span>{author}</span>
         <button
          onClick={() => handleRemoveSpecialAuthor(author)}
          className="text-slate-400 hover:text-slate-200"
         >
          <XCircle className="h-3 w-3" />
         </button>
        </div>
       ))}
      </div>
     </div>
    )}

    {/* Кнопки */}
    <div className="flex gap-2">
     <Button onClick={onReset} variant="outline" size="sm">
      Сбросить
     </Button>
    </div>
   </CardContent>
  </Card>
 )
} 