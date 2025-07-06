'use client'

import React, { useState } from 'react'
import {
  useKeywords,
  useCreateKeyword,
  useUpdateKeyword,
  useDeleteKeyword,
} from '@/hooks/use-keywords'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { Plus, Trash2, Search, Check, X } from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { KeywordResponse, KeywordUpdate } from '@/types/api'
import useDebounce from '@/hooks/use-debounce'

const KeywordRow = ({
  keyword,
  onUpdate,
  onDelete,
  isUpdating,
  isDeleting,
}: {
  keyword: KeywordResponse
  onUpdate: (id: number, data: KeywordUpdate) => void
  onDelete: (id: number) => void
  isUpdating: boolean
  isDeleting: boolean
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editedWord, setEditedWord] = useState(keyword.word)
  const debouncedWord = useDebounce(editedWord, 500)

  React.useEffect(() => {
    if (isEditing && debouncedWord !== keyword.word) {
      onUpdate(keyword.id, { word: debouncedWord })
    }
  }, [debouncedWord, isEditing, keyword.id, keyword.word, onUpdate])

  const handleSave = () => {
    if (editedWord !== keyword.word) {
      onUpdate(keyword.id, { word: editedWord })
    }
    setIsEditing(false)
  }

  return (
    <TableRow key={keyword.id}>
      <TableCell>
        {isEditing ? (
          <div className="flex items-center gap-2">
            <Input
              value={editedWord}
              onChange={(e) => setEditedWord(e.target.value)}
              className="h-8"
            />
            <Button size="icon" className="h-8 w-8" onClick={handleSave}>
              <Check className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8"
              onClick={() => setIsEditing(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <span
            className="cursor-pointer"
            onClick={() => setIsEditing(true)}
            title="Нажмите, чтобы редактировать"
          >
            {keyword.word}
          </span>
        )}
      </TableCell>
      <TableCell>
        <Badge variant="secondary">{keyword.total_matches}</Badge>
      </TableCell>
      <TableCell>
        <Switch
          checked={keyword.is_active}
          onCheckedChange={(isActive) =>
            onUpdate(keyword.id, { is_active: isActive })
          }
          disabled={isUpdating}
        />
      </TableCell>
      <TableCell className="text-right">
        <Button
          variant="ghost"
          size="icon"
          className="text-red-500 hover:text-red-400"
          onClick={() => onDelete(keyword.id)}
          disabled={isDeleting}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </TableCell>
    </TableRow>
  )
}

export default function KeywordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [newKeyword, setNewKeyword] = useState('')

  const { data: keywordsData, isLoading, error } = useKeywords()
  const createKeywordMutation = useCreateKeyword()
  const updateKeywordMutation = useUpdateKeyword()
  const deleteKeywordMutation = useDeleteKeyword()

  const handleAddKeyword = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!newKeyword.trim()) return
    toast.promise(
      createKeywordMutation.mutateAsync({
        word: newKeyword,
        is_active: true,
        is_case_sensitive: false,
        is_whole_word: false,
      }),
      {
        loading: 'Добавляем слово...',
        success: () => {
          setNewKeyword('')
          return 'Слово добавлено!'
        },
        error: 'Не удалось добавить слово.',
      }
    )
  }

  const handleDeleteKeyword = (id: number) => {
    toast.promise(deleteKeywordMutation.mutateAsync(id), {
      loading: 'Удаляем слово...',
      success: 'Слово удалено!',
      error: 'Не удалось удалить слово.',
    })
  }

  const handleUpdateKeyword = (id: number, data: KeywordUpdate) => {
    updateKeywordMutation.mutate({ keywordId: id, data })
  }

  const filteredKeywords =
    keywordsData?.items?.filter((keyword) =>
      keyword.word.toLowerCase().includes(searchTerm.toLowerCase())
    ) || []

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner />
        </div>
      )
    }

    if (error) {
      return (
        <div className="text-center text-red-500 py-10">
          <p>Ошибка при загрузке ключевых слов.</p>
        </div>
      )
    }

    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Ключевое слово</TableHead>
            <TableHead>Найдено комментариев</TableHead>
            <TableHead>Статус</TableHead>
            <TableHead className="text-right">Действия</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredKeywords.map((keyword) => (
            <KeywordRow
              key={keyword.id}
              keyword={keyword}
              onUpdate={handleUpdateKeyword}
              onDelete={handleDeleteKeyword}
              isUpdating={updateKeywordMutation.isPending}
              isDeleting={deleteKeywordMutation.isPending}
            />
          ))}
        </TableBody>
      </Table>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Ключевые слова</CardTitle>
        <CardDescription>
          Добавляйте и управляйте ключевыми словами для поиска в комментариях.
        </CardDescription>
        <div className="flex justify-between items-center pt-4">
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Поиск по словам..."
              className="pl-9"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <form
            onSubmit={handleAddKeyword}
            className="flex w-full max-w-sm items-center space-x-2"
          >
            <Input
              placeholder="Новое слово или фраза..."
              value={newKeyword}
              onChange={(e) => setNewKeyword(e.target.value)}
              disabled={createKeywordMutation.isPending}
            />
            <Button type="submit" disabled={createKeywordMutation.isPending}>
              <Plus className="mr-2 h-4 w-4" />
              Добавить
            </Button>
          </form>
        </div>
      </CardHeader>
      <CardContent>{renderContent()}</CardContent>
    </Card>
  )
}
