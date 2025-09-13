'use client'

import { useState, useRef } from 'react'

import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'

import { Alert, AlertDescription } from '@/shared/ui/alert'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
  DialogFooter,
} from '@/shared/ui/dialog'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Progress } from '@/shared/ui/progress'

export interface FileUploadModalProps {
  /** Тип загрузки - для определения API endpoint и параметров */
  type: 'groups' | 'keywords'
  /** Текст кнопки-триггера */
  triggerText?: string
  /** Заголовок модального окна */
  title?: string
  /** Описание формата файла */
  description?: string
  /** Callback при успешной загрузке */
  onSuccess?: () => void
  /** Дополнительные параметры для API */
  apiParams?: Record<string, any>
}

export function FileUploadModal({
  type,
  triggerText = 'Загрузить из файла',
  title,
  description,
  onSuccess,
  apiParams = {},
}: FileUploadModalProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>(
    'idle'
  )
  const [errorMessage, setErrorMessage] = useState('')
  const [uploadResults, setUploadResults] = useState<{
    created: number
    skipped: number
    errors: string[]
  } | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)

  const defaultTitles = {
    groups: 'Загрузка групп из файла',
    keywords: 'Загрузка ключевых слов из файла',
  }

  const defaultDescriptions = {
    groups:
      'Поддерживаемые форматы: CSV (screen_name,name,description) или TXT (одно screen_name на строку)',
    keywords:
      'Поддерживаемые форматы: CSV (word,category,description) или TXT (одно слово на строку)',
  }

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    await uploadFile(file)
  }

  const uploadFile = async (file: File) => {
    setIsUploading(true)
    setUploadStatus('uploading')
    setUploadProgress(0)
    setErrorMessage('')
    setUploadResults(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      // Добавляем дополнительные параметры
      Object.entries(apiParams).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          formData.append(key, value.toString())
        }
      })

      // Определяем endpoint в зависимости от типа
      const endpoint = type === 'groups' ? '/api/v1/groups/upload' : '/api/v1/keywords/upload'

      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()

      setUploadStatus('success')
      setUploadProgress(100)
      setUploadResults({
        created: result.created || 0,
        skipped: result.skipped || 0,
        errors: result.errors || [],
      })

      // Вызываем callback при успешной загрузке
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('error')
      setErrorMessage(error instanceof Error ? error.message : 'Произошла неизвестная ошибка')
    } finally {
      setIsUploading(false)
    }
  }

  const handleClose = () => {
    if (!isUploading) {
      setIsOpen(false)
      setUploadStatus('idle')
      setUploadProgress(0)
      setErrorMessage('')
      setUploadResults(null)
      // Сбрасываем input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleRetry = () => {
    setUploadStatus('idle')
    setUploadProgress(0)
    setErrorMessage('')
    setUploadResults(null)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" disabled={isUploading}>
          <Upload className="mr-2 h-4 w-4" />
          {triggerText}
        </Button>
      </DialogTrigger>

      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{title || defaultTitles[type]}</DialogTitle>
          <DialogDescription>{description || defaultDescriptions[type]}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Статус загрузки */}
          {uploadStatus === 'uploading' && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                <span className="text-sm">Загрузка файла...</span>
              </div>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          )}

          {/* Результат успешной загрузки */}
          {uploadStatus === 'success' && uploadResults && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                <div className="space-y-1">
                  <div>Файл успешно загружен!</div>
                  <div className="flex gap-2 text-xs">
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      Создано: {uploadResults.created}
                    </Badge>
                    {uploadResults.skipped > 0 && (
                      <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                        Пропущено: {uploadResults.skipped}
                      </Badge>
                    )}
                  </div>
                  {uploadResults.errors.length > 0 && (
                    <div className="text-xs text-yellow-700 mt-2">
                      <div className="font-medium">Предупреждения:</div>
                      <ul className="list-disc list-inside">
                        {uploadResults.errors.slice(0, 3).map((error, index) => (
                          <li key={index}>{error}</li>
                        ))}
                        {uploadResults.errors.length > 3 && (
                          <li>... и ещё {uploadResults.errors.length - 3} ошибок</li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Ошибка загрузки */}
          {uploadStatus === 'error' && (
            <Alert className="border-destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {/* Input для файла */}
          {uploadStatus === 'idle' && (
            <div className="space-y-2">
              <Label htmlFor="file-upload">Выберите файл</Label>
              <Input
                id="file-upload"
                ref={fileInputRef}
                type="file"
                accept=".txt,.csv"
                onChange={handleFileSelect}
                disabled={isUploading}
              />
            </div>
          )}
        </div>

        <DialogFooter>
          {uploadStatus === 'error' && (
            <Button variant="outline" onClick={handleRetry}>
              Попробовать снова
            </Button>
          )}
          <Button variant="outline" onClick={handleClose} disabled={isUploading}>
            {uploadStatus === 'success' ? 'Закрыть' : 'Отмена'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
