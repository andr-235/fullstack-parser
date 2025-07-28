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
import { useUploadGroupsWithProgress } from '@/entities/group'
import {
  Upload,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2,
} from 'lucide-react'
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
  const [uploadStatus, setUploadStatus] = useState<
    'idle' | 'uploading' | 'success' | 'error'
  >('idle')

  // Новые состояния для отслеживания прогресса
  const [currentGroup, setCurrentGroup] = useState<string>('')
  const [totalGroups, setTotalGroups] = useState(0)
  const [processedGroups, setProcessedGroups] = useState(0)
  const [uploadError, setUploadError] = useState<string>('')

  const uploadMutation = useUploadGroupsWithProgress()

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
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
    setCurrentGroup('Инициализация...')

    try {
      const result = await uploadMutation.mutateAsync({
        file: selectedFile,
        options: {
          is_active: isActive,
          max_posts_to_check: maxPostsToCheck,
        },
        onProgress: (progress) => {
          setUploadProgress(progress.progress)
          setCurrentGroup(progress.current_group)
          setTotalGroups(progress.total_groups)
          setProcessedGroups(progress.processed_groups)

          // Обновляем результат в реальном времени
          if (progress.status === 'completed') {
            setUploadResult({
              status: 'success',
              message: 'Загрузка завершена',
              total_processed: progress.total_groups,
              created: progress.created,
              skipped: progress.skipped,
              errors: progress.errors,
              created_groups: [],
            })
          }
        },
      })

      setUploadResult(result)
      setUploadStatus('success')
      setUploadProgress(100)
      setCurrentGroup('')

      toast.success(`Успешно загружено ${result.created} групп`)
      onSuccess?.()
    } catch (error: any) {
      setUploadStatus('error')
      setCurrentGroup('')

      // Детальная обработка ошибок
      let errorMessage = 'Ошибка загрузки'

      if (error?.response?.status) {
        switch (error.response.status) {
          case 404:
            errorMessage =
              'Сервер недоступен. Проверьте подключение к интернету'
            break
          case 413:
            errorMessage = 'Файл слишком большой. Максимальный размер: 5MB'
            break
          case 422:
            errorMessage =
              'Некорректный формат файла. Проверьте структуру данных'
            break
          case 500:
            errorMessage = 'Ошибка сервера. Попробуйте позже'
            break
          default:
            errorMessage = `Ошибка сервера (${error.response.status})`
        }
      } else if (error?.message) {
        if (error.message.includes('Network Error')) {
          errorMessage = 'Ошибка сети. Проверьте подключение к интернету'
        } else if (error.message.includes('timeout')) {
          errorMessage = 'Превышено время ожидания. Попробуйте позже'
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

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2">
          <Upload className="h-4 w-4" />
          Загрузить группы
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Загрузка групп из файла</DialogTitle>
          <DialogDescription>
            Загрузите файл с группами ВКонтакте для мониторинга
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Загрузка файла */}
          <div className="space-y-2">
            <Label htmlFor="file">Файл с группами</Label>
            <FileUpload
              onFileSelect={handleFileSelect}
              acceptedFileTypes={['.csv', '.txt']}
              maxSize={5 * 1024 * 1024}
            />
            {selectedFile && (
              <p className="text-sm text-gray-600">
                Выбран файл: {selectedFile.name} (
                {(selectedFile.size / 1024).toFixed(1)} KB)
              </p>
            )}
          </div>

          {/* Настройки */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Switch
                id="is-active"
                checked={isActive}
                onCheckedChange={setIsActive}
              />
              <Label htmlFor="is-active">Активные группы</Label>
            </div>

            <div className="space-y-2">
              <Label htmlFor="max-posts">
                Максимальное количество постов для проверки
              </Label>
              <Input
                id="max-posts"
                type="number"
                value={maxPostsToCheck}
                onChange={(e) => setMaxPostsToCheck(Number(e.target.value))}
                min={1}
                max={1000}
              />
            </div>
          </div>

          {/* Статус загрузки */}
          {(uploadStatus === 'uploading' ||
            uploadStatus === 'success' ||
            uploadStatus === 'error') && (
            <div className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-center gap-2 mb-3">
                {getStatusIcon()}
                <h4
                  className={`font-medium ${
                    uploadStatus === 'success'
                      ? 'text-green-700'
                      : uploadStatus === 'error'
                        ? 'text-red-700'
                        : 'text-blue-700'
                  }`}
                >
                  {getStatusText()}
                </h4>
              </div>

              {uploadStatus === 'uploading' && (
                <div className="space-y-2">
                  <Progress value={uploadProgress} className="w-full" />
                  <p className="text-sm text-gray-600">
                    {currentGroup ? (
                      <>
                        Обрабатывается:{' '}
                        <span className="font-medium">{currentGroup}</span>
                        {totalGroups > 0 && (
                          <span className="text-gray-500">
                            {' '}
                            ({processedGroups}/{totalGroups})
                          </span>
                        )}
                      </>
                    ) : (
                      'Подготовка к загрузке...'
                    )}
                  </p>
                </div>
              )}

              {uploadStatus === 'success' && uploadResult && (
                <div className="space-y-2">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-green-600">
                        Создано:
                      </span>{' '}
                      {uploadResult.created}
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">
                        Пропущено:
                      </span>{' '}
                      {uploadResult.skipped}
                    </div>
                  </div>
                </div>
              )}

              {uploadStatus === 'error' && uploadError && (
                <div className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                  <AlertCircle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                  <div className="text-sm text-red-700">
                    <p className="font-medium">Ошибка загрузки:</p>
                    <p>{uploadError}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={uploadStatus === 'uploading'}
          >
            Отмена
          </Button>
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || uploadStatus === 'uploading'}
            className="gap-2"
          >
            {uploadStatus === 'uploading' && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            Загрузить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
