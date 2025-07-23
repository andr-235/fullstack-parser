import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import type {
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
  PaginationParams,
} from '@/types/api'

/**
 * Хук для получения списка ключевых слов
 */
export function useKeywords(
  params?: PaginationParams & {
    active_only?: boolean
    category?: string
    q?: string
  }
) {
  return useQuery({
    queryKey: createQueryKey.keywords(params),
    queryFn: () => api.getKeywords(params),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

/**
 * Хук для получения конкретного ключевого слова
 */
export function useKeyword(keywordId: number) {
  return useQuery({
    queryKey: createQueryKey.keyword(keywordId),
    queryFn: () => api.getKeyword(keywordId),
    enabled: !!keywordId,
  })
}

/**
 * Хук для получения категорий ключевых слов
 */
export function useKeywordCategories() {
  return useQuery({
    queryKey: createQueryKey.keywordCategories(),
    queryFn: () => api.getKeywordCategories(),
    staleTime: 30 * 60 * 1000, // 30 минут
  })
}

/**
 * Хук для создания ключевого слова
 */
export function useCreateKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: KeywordCreate) => api.createKeyword(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      queryClient.invalidateQueries({ queryKey: ['keywords', 'categories'] })
    },
  })
}

/**
 * Хук для массового создания ключевых слов
 */
export function useCreateKeywordsBulk() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: KeywordCreate[]) => api.createKeywordsBulk(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      queryClient.invalidateQueries({ queryKey: ['keywords', 'categories'] })
    },
  })
}

/**
 * Хук для обновления ключевого слова
 */
export function useUpdateKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      keywordId,
      data,
    }: {
      keywordId: number
      data: KeywordUpdate
    }) => api.updateKeyword(keywordId, data),
    onSuccess: (_, { keywordId }) => {
      queryClient.invalidateQueries({ queryKey: ['keywords', keywordId] })
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

/**
 * Хук для удаления ключевого слова
 */
export function useDeleteKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (keywordId: number) => api.deleteKeyword(keywordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

/**
 * Хук для загрузки ключевых слов из файла
 */
export function useUploadKeywordsFromFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      file,
      options,
    }: {
      file: File
      options?: {
        default_category?: string
        is_active?: boolean
        is_case_sensitive?: boolean
        is_whole_word?: boolean
      }
    }) => api.uploadKeywordsFromFile(file, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      queryClient.invalidateQueries({ queryKey: ['keywords', 'categories'] })
    },
  })
}
