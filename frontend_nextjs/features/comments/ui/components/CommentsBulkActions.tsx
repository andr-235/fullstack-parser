'use client'

import React from 'react'
import { Button } from '@/shared/ui'
import { Badge } from '@/shared/ui'
import {
  Archive,
  ArchiveRestore,
  Eye,
  EyeOff,
  Trash2,
  CheckSquare,
  Square,
} from 'lucide-react'

interface CommentsBulkActionsProps {
  selectedComments: number[]
  totalComments: number
  onSelectAll: () => void
  onDeselectAll: () => void
  onMarkAsViewed: () => void
  onMarkAsUnviewed: () => void
  onArchive: () => void
  onUnarchive: () => void
  onDelete: () => void
  isProcessing: boolean
}

export function CommentsBulkActions({
  selectedComments,
  totalComments,
  onSelectAll,
  onDeselectAll,
  onMarkAsViewed,
  onMarkAsUnviewed,
  onArchive,
  onUnarchive,
  onDelete,
  isProcessing,
}: CommentsBulkActionsProps) {
  const isAllSelected =
    selectedComments.length === totalComments && totalComments > 0
  const isPartiallySelected =
    selectedComments.length > 0 && selectedComments.length < totalComments
  const hasSelected = selectedComments.length > 0

  const handleSelectToggle = () => {
    if (isAllSelected) {
      onDeselectAll()
    } else {
      onSelectAll()
    }
  }

  return (
    <div className="flex items-center justify-between p-4 bg-slate-800 border border-slate-700 rounded-lg">
      <div className="flex items-center gap-4">
        {/* Чекбокс выбора */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleSelectToggle}
            className="flex items-center justify-center w-5 h-5 text-slate-400 hover:text-slate-200"
            disabled={isProcessing}
          >
            {isAllSelected ? (
              <CheckSquare className="w-5 h-5 text-blue-500" />
            ) : isPartiallySelected ? (
              <div className="w-5 h-5 border-2 border-blue-500 bg-blue-500 rounded flex items-center justify-center">
                <div className="w-2 h-2 bg-white rounded-sm" />
              </div>
            ) : (
              <Square className="w-5 h-5" />
            )}
          </button>
          <span className="text-sm text-slate-400">
            {hasSelected
              ? `${selectedComments.length} из ${totalComments}`
              : 'Выбрать все'}
          </span>
        </div>

        {/* Счетчик выбранных */}
        {hasSelected && (
          <Badge variant="secondary" className="bg-blue-500 text-white">
            {selectedComments.length} выбрано
          </Badge>
        )}
      </div>

      {/* Массовые действия */}
      {hasSelected && (
        <div className="flex items-center gap-2">
          <Button
            onClick={onMarkAsViewed}
            disabled={isProcessing}
            variant="outline"
            size="sm"
            className="flex items-center gap-1"
          >
            <Eye className="w-4 h-4" />
            Отметить просмотренными
          </Button>

          <Button
            onClick={onMarkAsUnviewed}
            disabled={isProcessing}
            variant="outline"
            size="sm"
            className="flex items-center gap-1"
          >
            <EyeOff className="w-4 h-4" />
            Отметить непросмотренными
          </Button>

          <Button
            onClick={onArchive}
            disabled={isProcessing}
            variant="outline"
            size="sm"
            className="flex items-center gap-1"
          >
            <Archive className="w-4 h-4" />
            Архивировать
          </Button>

          <Button
            onClick={onUnarchive}
            disabled={isProcessing}
            variant="outline"
            size="sm"
            className="flex items-center gap-1"
          >
            <ArchiveRestore className="w-4 h-4" />
            Разархивировать
          </Button>

          <Button
            onClick={onDelete}
            disabled={isProcessing}
            variant="destructive"
            size="sm"
            className="flex items-center gap-1"
          >
            <Trash2 className="w-4 h-4" />
            Удалить
          </Button>
        </div>
      )}
    </div>
  )
}
