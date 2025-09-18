'use client'

import { useState } from 'react'

import { formatDistanceToNow } from 'date-fns'
import {
  Hash,
  Settings,
  Trash2,
  Edit,
  Power,
  PowerOff,
  MoreHorizontal,
  Calendar,
  MessageSquare,
} from 'lucide-react'

import { Keyword } from '@/entities/keywords'
import { KeywordForm, type KeywordFormData } from '@/features/keywords/ui/KeywordForm'

interface KeywordCardProps {
  keyword: Keyword
  onUpdate?: (id: number, updates: KeywordFormData) => void
  onDelete?: (id: number) => void
  onToggleStatus?: (id: number, isActive: boolean) => void
}

export function KeywordCard({ keyword, onUpdate, onDelete, onToggleStatus }: KeywordCardProps) {
  const [showEditForm, setShowEditForm] = useState(false)

  const handleUpdate = async (updates: KeywordFormData) => {
    if (onUpdate) {
      try {
        await onUpdate(Number(keyword.id), updates)
        setShowEditForm(false)
      } catch (err) {
        console.error('Failed to update keyword:', err)
      }
    }
  }

  const handleDelete = async () => {
    if (onDelete && confirm('Вы уверены, что хотите удалить это ключевое слово?')) {
      try {
        await onDelete(Number(keyword.id))
      } catch (err) {
        console.error('Failed to delete keyword:', err)
      }
    }
  }

  const handleToggleStatus = async () => {
    if (onToggleStatus) {
      try {
        await onToggleStatus(Number(keyword.id), !keyword.status.is_active)
      } catch (err) {
        console.error('Failed to toggle keyword status:', err)
      }
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg group hover:shadow-md transition-shadow">
      <div className="p-6 pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-100">
              <Hash className="h-5 w-5 text-blue-600" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-sm font-medium truncate">"{keyword.name}"</h3>
              <p className="text-xs text-gray-500">
                {keyword.category?.name || 'Без категории'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 text-xs rounded-full ${
              keyword.status.is_active 
                ? 'bg-green-100 text-green-800' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              {keyword.status.is_active ? 'Активное' : 'Неактивное'}
            </span>

            <div className="relative">
              <button
                onClick={() => setShowEditForm(true)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-gray-100 rounded"
              >
                <MoreHorizontal className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 pt-0 pb-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-gray-400" />
            <span className="text-sm">
              {(keyword.total_matches || keyword.match_count || 0).toLocaleString()} совпадений
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <span className="text-sm">
              {formatDistanceToNow(new Date(keyword.created_at), { addSuffix: true })}
            </span>
          </div>
        </div>

        {keyword.description && (
          <p className="text-xs text-gray-500 line-clamp-2">{keyword.description}</p>
        )}

        <div className="flex items-center gap-2 pt-2">
          <button
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-2"
            onClick={() => {
              console.log('Navigate to matches for keyword:', keyword.id)
            }}
          >
            <MessageSquare className="h-3 w-3" />
            Показать совпадения
          </button>

          <button
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
            onClick={() => setShowEditForm(true)}
          >
            <Edit className="h-3 w-3" />
          </button>

          <button
            className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
            onClick={handleToggleStatus}
          >
            {keyword.status.is_active ? (
              <PowerOff className="h-3 w-3" />
            ) : (
              <Power className="h-3 w-3" />
            )}
          </button>

          <button
            className="px-3 py-2 text-sm border border-red-300 text-red-600 rounded-md hover:bg-red-50"
            onClick={handleDelete}
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      </div>

      {showEditForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium">Редактировать ключевое слово</h2>
            </div>
            <div className="p-6">
              <KeywordForm
                initialData={{
                  name: keyword.name || '',
                  category: keyword.category?.name || '',
                  description: keyword.description || '',
                  is_active: keyword.status.is_active,
                }}
                onSubmit={handleUpdate}
                onCancel={() => setShowEditForm(false)}
                submitLabel="Обновить ключевое слово"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
