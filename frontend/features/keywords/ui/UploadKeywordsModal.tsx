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
import { useUploadKeywordsWithProgress } from '@/entities/keyword'
import { Upload, AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { toast } from 'react-hot-toast'
import type { KeywordUploadResponse } from '@/types/api'

interface UploadKeywordsModalProps {
  onSuccess?: () => void
}

export default function UploadKeywordsModal({
  onSuccess,
}: UploadKeywordsModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [defaultCategory, setDefaultCategory] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [isCaseSensitive, setIsCaseSensitive] = useState(false)
  const [isWholeWord, setIsWholeWord] = useState(false)
  const [uploadResult, setUploadResult] =
    useState<KeywordUploadResponse | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')

  // Новые состояния для отслеживания прогресса
  const [currentKeyword, setCurrentKeyword] = useState<string>('')
  const [totalKeywords, setTotalKeywords] = useState(0)
  const [processedKeywords, setProcessedKeywords] = useState(0)
  const [uploadError, setUploadError] = useState<string>('')

  const uploadMutation = useUploadKeywordsWithProgress()

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
    setCurrentKeyword('Инициализация...')

    try {
      const result = await uploadMutation.mutateAsync({
        file: selectedFile,
        options: {
          default_category: defaultCategory,
          is_active: isActive,
          is_case_sensitive: isCaseSensitive,
          is_whole_word: isWholeWord,
        },
        onProgress: (progress) => {
          setUploadProgress(progress.progress)
          setCurrentKeyword(progress.current_keyword)
          setTotalKeywords(progress.total_keywords)
          setProcessedKeywords(progress.processed_keywords)

          // Обновляем результат в реальном времени
          if (progress.status === 'completed') {
            setUploadResult({
              status: 'success',
              message: 'Загрузка завершена',
              total_processed: progress.total_keywords,
              created: progress.created,
              skipped: progress.skipped,
              errors: progress.errors,
              created_keywords: [],
            })
          }
        },
      })

      setUploadResult(result)
      setUploadStatus('success')
      setUploadProgress(100)
      setCurrentKeyword('')

      toast.success(`Успешно загружено ${result.created} ключевых слов`)
      onSuccess?.()
    } catch (error: any) {
      setUploadStatus('error')
      setCurrentKeyword('')

      // Детальная обработка ошибок
      let errorMessage = 'Ошибка загрузки'

      if (error?.response?.status) {
        switch (error.response.status) {
          case 404:
            errorMessage = 'Сервер недоступен. Проверьте подключение к интернету'
            break
          case 413:
            errorMessage = 'Файл слишком большой. Максимальный размер: 5MB'
            break
          case 422:
            errorMessage = 'Некорректный формат файла. Проверьте структуру данных'
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
        } else if (error.message.includes('FILE_ERROR_NO_SPACE')) {
          errorMessage = 'Недостаточно места на диске. Обратитесь к администратору'
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
    setDefaultCategory('')
    setIsActive(true)
    setIsCaseSensitive(false)
    setIsWholeWord(false)
    setUploadResult(null)
    setUploadProgress(0)
    setUploadStatus('idle')
    setCurrentKeyword('')
    setTotalKeywords(0)
    setProcessedKeywords(0)
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
        return 'Обработка ключевых слов...'
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
            {selectedFile && (
              <p className="text-sm text-gray-600 mt-2">
                Выбран файл: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
              </p>
            )}
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
                  <Progress value={uploadProgress} className="w-full" />
                  <p className="text-sm text-gray-600">
                    {currentKeyword ? (
                      <>
                        Обрабатывается: <span className="font-medium">{currentKeyword}</span>
                        {totalKeywords > 0 && (
                          <span className="text-gray-500">
                            {' '}({processedKeywords}/{totalKeywords})
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
                      <span className="font-medium text-green-600">Создано:</span> {uploadResult.created}
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Пропущено:</span> {uploadResult.skipped}
                    </div>
                  </div>
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
            {uploadStatus === 'uploading' && <Loader2 className="h-4 w-4 animate-spin" />}
            Загрузить
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
