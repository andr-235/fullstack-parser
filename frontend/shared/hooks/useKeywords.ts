/**
 * Хуки для работы с ключевыми словами
 */

import { useCreate, useReadList, useReadOne, useUpdate, useDelete } from './useCrud'
import type { Keyword, KeywordsResponse, CreateKeywordRequest, UpdateKeywordRequest, KeywordsFilters } from '@/entities/keywords'

// Хук для создания ключевого слова
export function useCreateKeyword() {
  return useCreate<Keyword, CreateKeywordRequest>('/api/v1/keywords', {
    successMessage: 'Ключевое слово успешно создано',
    errorMessage: 'Ошибка при создании ключевого слова',
  })
}

// Хук для получения списка ключевых слов
export function useKeywords(params?: KeywordsFilters) {
  return useReadList<KeywordsResponse>('/api/v1/keywords', params as Record<string, unknown>)
}

// Хук для получения одного ключевого слова
export function useKeyword(id: number) {
  return useReadOne<Keyword>('/api/v1/keywords', id)
}

// Хук для обновления ключевого слова
export function useUpdateKeyword(id: number) {
  return useUpdate<Keyword, UpdateKeywordRequest>(`/api/v1/keywords/${id}`, {
    successMessage: 'Ключевое слово успешно обновлено',
    errorMessage: 'Ошибка при обновлении ключевого слова',
  })
}

// Хук для удаления ключевого слова
export function useDeleteKeyword(id: number) {
  return useDelete<Keyword>(`/api/v1/keywords/${id}`, {
    successMessage: 'Ключевое слово успешно удалено',
    errorMessage: 'Ошибка при удалении ключевого слова',
  })
}