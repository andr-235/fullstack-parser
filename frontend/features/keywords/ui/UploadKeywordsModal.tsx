'use client'

import React, { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { FileUpload } from '@/components/ui/file-upload'
import { useUploadKeywordsFromFile } from '@/features/keywords/hooks/use-keywords'
import { Upload, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { KeywordUploadResponse } from '@/types/api'

interface UploadKeywordsModalProps {
  onSuccess?: () => void
}

export default function UploadKeywordsModal({ onSuccess }: UploadKeywordsModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [defaultCategory, setDefaultCategory] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [isCaseSensitive, setIsCaseSensitive] = useState(false)
  const [isWholeWord, setIsWholeWord] = useState(false)
  const [uploadResult, setUploadResult] =
    useState<KeywordUploadResponse | null>(null)

  const uploadMutation = useUploadKeywordsFromFile()

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setUploadResult(null)
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Выберите файл для загрузки')
      return
    }

    // Проверяем размер файла
    if (selectedFile.size > 5 * 1024 * 1024) {
      toast.error('Файл слишком большой. Максимальный размер: 5MB')
      return
    }

    // Проверяем тип файла
    const allowedTypes = ['.csv', '.txt']
    const fileExtension = selectedFile.name
      .toLowerCase()
      .substring(selectedFile.name.lastIndexOf('.'))
    if (!allowedTypes.includes(fileExtension)) {
      toast.error('Неподдерживаемый тип файла. Используйте CSV или TXT')
      return
    }

    try {
      const result = await uploadMutation.mutateAsync({
        file: selectedFile,
        options: {
          default_category: defaultCategory || undefined,
          is_active: isActive,
          is_case_sensitive: isCaseSensitive,
          is_whole_word: isWholeWord,
        },
      })

      setUploadResult(result)
      toast.success(result.message)

      if (onSuccess) {
        onSuccess()
      }

      // Закрываем модальное окно через 2 секунды
      setTimeout(() => {
        setIsOpen(false)
        resetForm()
      }, 2000)
    } catch (error) {
      console.error('Upload error:', error)

      // Улучшенная обработка ошибок
      let errorMessage = 'Ошибка загрузки файла'

      if (error instanceof Error) {
        if (error.message.includes('FILE_ERROR_NO_SPACE')) {
          errorMessage =
            'Недостаточно места на диске. Обратитесь к администратору.'
        } else if (error.message.includes('404')) {
          errorMessage = 'Сервер недоступен. Попробуйте позже.'
        } else if (error.message.includes('413')) {
          errorMessage = 'Файл слишком большой.'
        } else {
          errorMessage = error.message
        }
      }

      toast.error(errorMessage)
    }
  }

  const resetForm = () => {
    setSelectedFile(null)
    setDefaultCategory('')
    setIsActive(true)
    setIsCaseSensitive(false)
    setIsWholeWord(false)
    setUploadResult(null)
  }

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      resetForm()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Upload className="h-4 w-4" />
          Загрузить из файла
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Загрузка ключевых слов из файла</DialogTitle>
          <DialogDescription>
            Загрузите ключевые слова из CSV или TXT файла. Поддерживаются
            форматы:
            <br />
            • CSV: word,category,description
            <br />• TXT: одно слово на строку
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Загрузка файла */}
          <div>
            <Label>Файл с ключевыми словами</Label>
            <FileUpload
              onFileSelect={handleFileSelect}
              acceptedFileTypes={['.csv', '.txt']}
              maxSize={5 * 1024 * 1024} // 5MB
              className="mt-2"
              placeholder="Перетащите CSV или TXT файл сюда"
            />
          </div>

          {/* Настройки */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="category">Категория по умолчанию</Label>
              <Input
                id="category"
                value={defaultCategory}
                onChange={(e) => setDefaultCategory(e.target.value)}
                placeholder="Например: Общие"
                className="mt-1"
              />
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label htmlFor="is-active">Активные ключевые слова</Label>
              <Switch
                id="is-active"
                checked={isActive}
                onCheckedChange={setIsActive}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="case-sensitive">Учитывать регистр</Label>
              <Switch
                id="case-sensitive"
                checked={isCaseSensitive}
                onCheckedChange={setIsCaseSensitive}
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="whole-word">Только целые слова</Label>
              <Switch
                id="whole-word"
                checked={isWholeWord}
                onCheckedChange={setIsWholeWord}
              />
            </div>
          </div>

          {/* Результат загрузки */}
          {uploadResult && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <h4 className="font-medium text-green-700">
                  Загрузка завершена
                </h4>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <strong>Обработано строк:</strong>{' '}
                  {uploadResult.total_processed}
                </p>
                <p>
                  <strong>Создано:</strong> {uploadResult.created}
                </p>
                <p>
                  <strong>Пропущено (дубликаты):</strong> {uploadResult.skipped}
                </p>
                {uploadResult.errors.length > 0 && (
                  <div>
                    <p className="font-medium text-red-600">Ошибки:</p>
                    <ul className="list-disc list-inside text-red-600 space-y-1">
                      {uploadResult.errors.map((error, index) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Кнопки */}
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Отмена
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || uploadMutation.isPending}
            >
              {uploadMutation.isPending ? 'Загрузка...' : 'Загрузить'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
