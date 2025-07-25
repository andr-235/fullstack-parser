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
import { Progress } from '@/shared/ui'
import { useUploadGroupsFromFile } from '@/entities/group'
import { Upload, AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { VKGroupUploadResponse } from '@/types/api'

interface UploadGroupsModalProps {
  onSuccess?: () => void
}

export function UploadGroupsModal({ onSuccess }: UploadGroupsModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isActive, setIsActive] = useState(true)
  const [maxPostsToCheck, setMaxPostsToCheck] = useState(100)
  const [uploadResult, setUploadResult] =
    useState<VKGroupUploadResponse | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')

  // Новые состояния для отслеживания прогресса
  const [currentGroup, setCurrentGroup] = useState<string>('')
  const [totalGroups, setTotalGroups] = useState(0)
  const [processedGroups, setProcessedGroups] = useState(0)
  const [uploadError, setUploadError] = useState<string>('')

  const uploadMutation = useUploadGroupsFromFile()

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setUploadResult(null)
    setUploadProgress(0)
    setUploadStatus('idle')
    setCurrentGroup('')
    setTotalGroups(0)
    setProcessedGroups(0)
    setUploadError('')
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

    // Начинаем загрузку
    setUploadStatus('uploading')
    setUploadProgress(0)
    setUploadError('')

    // Читаем файл для подсчета групп
    const fileContent = await selectedFile.text()
    const lines = fileContent.split('\n').filter(line => line.trim())
    const estimatedGroups = lines.length
    setTotalGroups(estimatedGroups)
    setProcessedGroups(0)
    setCurrentGroup('Подготовка файла...')

    let progressInterval: NodeJS.Timeout | null = null

    try {
      // Симуляция прогресса с информацией о группах
      progressInterval = setInterval(() => {
        setProcessedGroups(prev => {
          const newProcessed = Math.min(prev + 1, estimatedGroups)
          const progress = Math.round((newProcessed / estimatedGroups) * 90)
          setUploadProgress(progress)

          // Симулируем название текущей группы
          if (newProcessed <= estimatedGroups) {
            const currentLine = lines[newProcessed - 1] || ''
            const groupName = currentLine.split(',')[1] || currentLine.split(',')[0] || `Группа ${newProcessed}`
            setCurrentGroup(groupName.trim())
          }

          if (newProcessed >= estimatedGroups) {
            if (progressInterval) clearInterval(progressInterval)
            return estimatedGroups
          }
          return newProcessed
        })
      }, 800) // Увеличили интервал для более заметного прогресса

      const response = await uploadMutation.mutateAsync({
        file: selectedFile,
        options: {
          is_active: isActive,
          max_posts_to_check: maxPostsToCheck,
        },
      })

      // Извлекаем данные из ответа API
      const result = response.data as VKGroupUploadResponse

      if (progressInterval) clearInterval(progressInterval)
      setUploadProgress(100)
      setUploadStatus('success')
      setUploadResult(result)
      setCurrentGroup('Завершено')

      // Показываем результат
      if (result.created > 0) {
        toast.success(`Успешно создано ${result.created} групп`)
      }
      if (result.skipped > 0) {
        toast.success(`Пропущено ${result.skipped} дубликатов`)
      }
      if (result.errors && result.errors.length > 0) {
        toast.error(`Ошибок: ${result.errors.length}`)
      }

      if (onSuccess) {
        onSuccess()
      }

      // Закрываем модальное окно через 5 секунд
      setTimeout(() => {
        setIsOpen(false)
        resetForm()
      }, 5000)
    } catch (error) {
      if (progressInterval) clearInterval(progressInterval)
      setUploadProgress(0)
      setUploadStatus('error')
      console.error('Upload error:', error)

      // Улучшенная обработка ошибок
      let errorMessage = 'Неизвестная ошибка загрузки'

      if (error instanceof Error) {
        if (error.message.includes('FILE_ERROR_NO_SPACE')) {
          errorMessage = 'Недостаточно места на диске. Обратитесь к администратору.'
        } else if (error.message.includes('404')) {
          errorMessage = 'Сервер недоступен. Попробуйте позже.'
        } else if (error.message.includes('413')) {
          errorMessage = 'Файл слишком большой.'
        } else if (error.message.includes('422')) {
          errorMessage = 'Некорректный формат файла. Проверьте структуру данных.'
        } else if (error.message.includes('500')) {
          errorMessage = 'Ошибка сервера. Попробуйте позже или обратитесь к администратору.'
        } else if (error.message.includes('Network Error')) {
          errorMessage = 'Ошибка сети. Проверьте подключение к интернету.'
        } else {
          errorMessage = error.message
        }
      }

      setUploadError(errorMessage)
      toast.error(errorMessage)
    }
  }

  const resetForm = () => {
    setSelectedFile(null)
    setIsActive(true)
    setMaxPostsToCheck(100)
    setUploadResult(null)
    setUploadProgress(0)
    setUploadStatus('idle')
    setCurrentGroup('')
    setTotalGroups(0)
    setProcessedGroups(0)
    setUploadError('')
  }

  const handleOpenChange = (open: boolean) => {
    setIsOpen(open)
    if (!open) {
      resetForm()
    }
  }

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return null
    }
  }

  const getStatusText = () => {
    switch (uploadStatus) {
      case 'uploading':
        return 'Обработка групп...'
      case 'success':
        return 'Загрузка завершена'
      case 'error':
        return 'Ошибка загрузки'
      default:
        return ''
    }
  }

  const getProgressText = () => {
    if (uploadStatus === 'uploading' && totalGroups > 0) {
      if (currentGroup) {
        return `${currentGroup} (${processedGroups}/${totalGroups})`
      }
      return `Обработано: ${processedGroups}/${totalGroups}`
    }
    return ''
  }

  const getProgressPercentage = () => {
    if (totalGroups > 0) {
      return Math.round((processedGroups / totalGroups) * 100)
    }
    return uploadProgress
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
          {/* Статус загрузки */}
          {(uploadStatus === 'uploading' || uploadStatus === 'success' || uploadStatus === 'error') && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center gap-2 mb-3">
                {getStatusIcon()}
                <h4 className={`font-medium ${uploadStatus === 'success' ? 'text-green-700' :
                  uploadStatus === 'error' ? 'text-red-700' :
                    'text-blue-700'
                  }`}>
                  {getStatusText()}
                </h4>
              </div>

              {uploadStatus === 'uploading' && (
                <div className="space-y-2">
                  <Progress value={getProgressPercentage()} className="w-full" />
                  <p className="text-sm text-gray-600">
                    {getProgressText()}
                  </p>
                  <p className="text-xs text-gray-500">
                    Прогресс: {getProgressPercentage()}%
                  </p>
                </div>
              )}

              {uploadStatus === 'error' && uploadError && (
                <div className="space-y-2">
                  <div className="flex items-start gap-2 p-3 bg-red-50 rounded border border-red-200">
                    <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                    <div className="text-sm text-red-700">
                      <p className="font-medium mb-1">Причина ошибки:</p>
                      <p>{uploadError}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Загрузка файла */}
          <div>
            <Label>Файл с группами</Label>
            <FileUpload
              onFileSelect={handleFileSelect}
              acceptedFileTypes={['.csv', '.txt']}
              maxSize={5 * 1024 * 1024} // 5MB
              className="mt-2"
              placeholder="Перетащите CSV или TXT файл сюда"
              disabled={uploadStatus === 'uploading'}
            />
          </div>

          {/* Настройки */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="is-active"
                checked={isActive}
                onCheckedChange={setIsActive}
                disabled={uploadStatus === 'uploading'}
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
                disabled={uploadStatus === 'uploading'}
              />
            </div>
          </div>

          {/* Детальный результат загрузки */}
          {uploadResult && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <h4 className="font-medium text-green-700">
                  Результат загрузки
                </h4>
              </div>

              {/* Статистика */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-green-100 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {uploadResult.total_processed}
                  </div>
                  <div className="text-sm text-green-700">Обработано</div>
                </div>
                <div className="text-center p-3 bg-blue-100 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {uploadResult.created}
                  </div>
                  <div className="text-sm text-blue-700">Создано</div>
                </div>
                <div className="text-center p-3 bg-yellow-100 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {uploadResult.skipped}
                  </div>
                  <div className="text-sm text-yellow-700">Пропущено</div>
                </div>
                <div className="text-center p-3 bg-red-100 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {uploadResult.errors?.length || 0}
                  </div>
                  <div className="text-sm text-red-700">Ошибок</div>
                </div>
              </div>

              {/* Созданные группы */}
              {uploadResult.created_groups && uploadResult.created_groups.length > 0 && (
                <div className="mb-4">
                  <h5 className="font-medium text-gray-700 mb-2">
                    Созданные группы:
                  </h5>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {uploadResult.created_groups.map((group, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{group.name}</div>
                          <div className="text-sm text-gray-500">@{group.screen_name}</div>
                        </div>
                        <div className="text-sm text-gray-500">
                          {group.members_count?.toLocaleString()} участников
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Ошибки */}
              {uploadResult.errors && uploadResult.errors.length > 0 && (
                <div>
                  <h5 className="font-medium text-red-600 mb-2">
                    Ошибки ({uploadResult.errors.length}):
                  </h5>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {uploadResult.errors.map((error, index) => (
                      <div key={index} className="flex items-start gap-2 p-2 bg-red-50 rounded border border-red-200">
                        <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-red-700">{error}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Кнопки */}
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={uploadStatus === 'uploading'}
            >
              Отмена
            </Button>
            <Button
              onClick={handleUpload}
              disabled={!selectedFile || uploadMutation.isPending || uploadStatus === 'uploading'}
            >
              {uploadStatus === 'uploading' ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Загрузка...
                </>
              ) : (
                'Загрузить'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
