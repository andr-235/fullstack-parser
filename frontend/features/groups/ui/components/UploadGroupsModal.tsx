'use client'

import React, { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Switch } from '@/shared/ui'
import { FileUpload } from '@/shared/ui'
import { useUploadGroupsFromFile } from '@/entities/group'
import { Upload, AlertCircle, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { VKGroupUploadResponse } from '@/types/api'

interface UploadGroupsModalProps {
  onSuccess?: () => void
}

export function UploadGroupsModal({
  onSuccess,
}: UploadGroupsModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isActive, setIsActive] = useState(true)
  const [maxPostsToCheck, setMaxPostsToCheck] = useState(100)
  const [uploadResult, setUploadResult] =
    useState<VKGroupUploadResponse | null>(null)

  const uploadMutation = useUploadGroupsFromFile()

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
          is_active: isActive,
          max_posts_to_check: maxPostsToCheck,
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
    setIsActive(true)
    setMaxPostsToCheck(100)
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
          <DialogTitle>Загрузка групп из файла</DialogTitle>
          <DialogDescription>
            Загрузите группы из CSV или TXT файла. Поддерживаются форматы:
            <br />
            • CSV: screen_name,name,description
            <br />• TXT: одно screen_name на строку
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Загрузка файла */}
          <div>
            <Label>Файл с группами</Label>
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
            <div className="flex items-center space-x-2">
              <Switch
                id="is-active"
                checked={isActive}
                onCheckedChange={setIsActive}
              />
              <Label htmlFor="is-active">Активные группы</Label>
            </div>
            <div>
              <Label htmlFor="max-posts">Максимум постов для проверки</Label>
              <Input
                id="max-posts"
                type="number"
                min="1"
                max="1000"
                value={maxPostsToCheck}
                onChange={(e) => setMaxPostsToCheck(Number(e.target.value))}
                className="mt-1"
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
