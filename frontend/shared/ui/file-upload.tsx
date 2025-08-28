'use client'

import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, FileText, FileSpreadsheet } from 'lucide-react'
import { cn } from '@/shared/lib/utils'
import { Button } from './button'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  acceptedFileTypes?: string[]
  maxSize?: number
  className?: string
  disabled?: boolean
  placeholder?: string
}

export function FileUpload({
  onFileSelect,
  acceptedFileTypes = ['.csv', '.txt'],
  maxSize = 5 * 1024 * 1024, // 5MB
  className,
  disabled = false,
  placeholder = 'Перетащите файл сюда или нажмите для выбора',
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0 && acceptedFiles[0]) {
        const file = acceptedFiles[0]
        setSelectedFile(file)
        onFileSelect(file)
      }
    },
    [onFileSelect]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      accept: acceptedFileTypes.reduce(
        (acc, type) => {
          acc[type] = []
          return acc
        },
        {} as Record<string, string[]>
      ),
      maxSize,
      multiple: false,
      disabled,
    })

  const removeFile = () => {
    setSelectedFile(null)
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'csv':
        return <FileSpreadsheet className="h-8 w-8 text-primary" />
      case 'txt':
        return <FileText className="h-8 w-8 text-green-600" />
      default:
        return <FileText className="h-8 w-8 text-muted-foreground" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className={cn('w-full', className)}>
      {!selectedFile ? (
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors',
            isDragActive && !isDragReject && 'border-primary bg-primary/5',
            isDragReject && 'border-destructive bg-destructive/5',
            disabled && 'opacity-50 cursor-not-allowed',
            'hover:border-muted-foreground'
          )}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-sm text-muted-foreground mb-2">{placeholder}</p>
          <p className="text-xs text-muted-foreground">
            Поддерживаемые форматы: {acceptedFileTypes.join(', ')}
          </p>
          <p className="text-xs text-muted-foreground">
            Максимальный размер: {formatFileSize(maxSize)}
          </p>
        </div>
      ) : (
        <div className="border rounded-lg p-4 bg-muted/30">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getFileIcon(selectedFile.name)}
              <div>
                <p className="text-sm font-medium text-foreground">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatFileSize(selectedFile.size)}
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={removeFile}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
