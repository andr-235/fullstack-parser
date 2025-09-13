'use client'

import { useState } from 'react'

import { KEYWORD_CATEGORIES } from '@/entities/keywords'

interface KeywordFormData {
  word: string;
  category?: string;
  description?: string;
  is_active?: boolean;
  is_case_sensitive?: boolean;
  is_whole_word?: boolean;
}

interface KeywordFormProps {
  initialData?: Partial<KeywordFormData>
  onSubmit: (data: KeywordFormData) => Promise<void>
  onCancel: () => void
  submitLabel?: string
}

export function KeywordForm({
  initialData,
  onSubmit,
  onCancel,
  submitLabel = 'Create Keyword',
}: KeywordFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState<KeywordFormData>({
    word: initialData?.word || '',
    category: initialData?.category || '',
    description: initialData?.description || '',
    is_active: initialData?.is_active ?? true,
    is_case_sensitive: initialData?.is_case_sensitive ?? false,
    is_whole_word: initialData?.is_whole_word ?? false,
  })
  const [errors, setErrors] = useState<Partial<KeywordFormData>>({})

  const validateForm = (): boolean => {
    const newErrors: Partial<KeywordFormData> = {}
    
    if (!formData.word.trim()) {
      newErrors.word = 'Ключевое слово обязательно'
    } else if (formData.word.length > 200) {
      newErrors.word = 'Ключевое слово слишком длинное'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    setIsSubmitting(true)
    try {
      await onSubmit(formData)
      setFormData({
        word: '',
        category: '',
        description: '',
        is_active: true,
        is_case_sensitive: false,
        is_whole_word: false,
      })
      setErrors({})
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Ключевое слово</label>
        <input
          type="text"
          placeholder="Введите ключевое слово для мониторинга..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={formData.word}
          onChange={e => setFormData({ ...formData, word: e.target.value })}
        />
        {errors.word && <p className="text-red-500 text-sm mt-1">{errors.word}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Категория (необязательно)</label>
        <select
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          value={formData.category || ''}
          onChange={e => setFormData({ ...formData, category: e.target.value })}
        >
          <option value="">Выберите категорию</option>
          {KEYWORD_CATEGORIES.map(category => (
            <option key={category.key} value={category.key}>
              {category.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Описание (необязательно)</label>
        <textarea
          placeholder="Опишите, для чего предназначено это ключевое слово..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[80px]"
          value={formData.description || ''}
          onChange={e => setFormData({ ...formData, description: e.target.value })}
        />
      </div>

      <div className="flex items-center justify-between rounded-lg border p-4">
        <div>
          <label className="text-base font-medium text-gray-700">Активный мониторинг</label>
          <p className="text-sm text-gray-500">Включить мониторинг комментариев для этого ключевого слова</p>
        </div>
        <input
          type="checkbox"
          checked={formData.is_active ?? true}
          onChange={e => setFormData({ ...formData, is_active: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
      </div>

      <div className="flex items-center justify-between rounded-lg border p-3">
        <div>
          <label className="text-base font-medium text-gray-700">Регистр</label>
          <p className="text-sm text-gray-500">Совпадение с точным регистром</p>
        </div>
        <input
          type="checkbox"
          checked={formData.is_case_sensitive ?? false}
          onChange={e => setFormData({ ...formData, is_case_sensitive: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
      </div>

      <div className="flex items-center justify-between rounded-lg border p-3">
        <div>
          <label className="text-base font-medium text-gray-700">Только целое слово</label>
          <p className="text-sm text-gray-500">Совпадение только с целыми словами</p>
        </div>
        <input
          type="checkbox"
          checked={formData.is_whole_word ?? false}
          onChange={e => setFormData({ ...formData, is_whole_word: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Отмена
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? 'Сохранение...' : submitLabel}
        </button>
      </div>
    </form>
  )
}
