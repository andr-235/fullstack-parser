/**
 * Оптимизированные хуки для работы с ключевыми словами
 *
 * Основные улучшения:
 * - Строгая типизация с TypeScript
 * - Централизованные query keys
 * - Утилиты для построения URL параметров
 * - Оптимизированная конфигурация кеширования
 * - Улучшенная обработка ошибок с retry логикой
 * - Оптимизированное управление кешем (setQueryData, removeQueries)
 * - Поддержка опциональных параметров для всех хуков
 * - Лучшие практики React Query v5
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
  type UseQueryOptions,
  type UseMutationOptions,
  type UseInfiniteQueryOptions,
} from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type {
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
  PaginatedResponse,
  PaginationParams,
  KeywordUploadResponse,
} from '@/types/api'

// Константы для лучшей типизации
const QUERY_KEYS = {
  keywords: 'keywords',
  keyword: 'keyword',
  categories: 'keyword-categories',
  totalMatches: 'total-matches',
  infiniteKeywords: 'infinite-keywords',
} as const

const ORDER_DIRECTIONS = ['asc', 'desc'] as const
type OrderDirection = (typeof ORDER_DIRECTIONS)[number]

// Базовые параметры для запросов
interface BaseKeywordsParams {
  active_only?: boolean
  category?: string
  q?: string
}

// Параметры для обычных запросов
export interface KeywordsParams extends PaginationParams, BaseKeywordsParams {
  page?: number
  size?: number
}

// Параметры для бесконечной прокрутки
export interface InfiniteKeywordsParams extends BaseKeywordsParams {
  pageSize?: number
  order_by?: string
  order_dir?: OrderDirection
}

// Утилита для построения URL параметров
function buildQueryParams(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      const stringValue =
        typeof value === 'string' ? value.trim() : String(value)
      if (stringValue) {
        searchParams.append(key, stringValue)
      }
    }
  })

  return searchParams.toString()
}

// Утилита для создания query keys
function createQueryKey(key: string, params?: Record<string, unknown>) {
  return params ? [key, params] : [key]
}

// Базовая конфигурация для запросов
const defaultQueryConfig = {
  staleTime: 5 * 60 * 1000, // 5 минут
  gcTime: 10 * 60 * 1000, // 10 минут (бывший cacheTime)
  retry: (failureCount: number, error: Error) => {
    // Не повторяем для 4xx ошибок, кроме 408, 429
    if (
      error.message.includes('4') &&
      !error.message.includes('408') &&
      !error.message.includes('429')
    ) {
      return false
    }
    return failureCount < 3
  },
  retryDelay: (attemptIndex: number) =>
    Math.min(1000 * 2 ** attemptIndex, 30000),
} as const

// Хук для получения списка ключевых слов
export function useKeywords(
  params?: KeywordsParams,
  options?: Omit<
    UseQueryOptions<PaginatedResponse<KeywordResponse>>,
    'queryKey' | 'queryFn'
  >
) {
  const { page = 1, size = 20, active_only, category, q } = params || {}

  const queryParams = {
    page,
    size,
    ...(active_only !== undefined && { active_only }),
    ...(category?.trim() && { category: category.trim() }),
    ...(q?.trim() && { q: q.trim() }),
  }

  return useQuery({
    queryKey: createQueryKey(QUERY_KEYS.keywords, queryParams),
    queryFn: () => {
      const searchParams = buildQueryParams(queryParams)
      return api.get<PaginatedResponse<KeywordResponse>>(
        `/api/v1/keywords?${searchParams}`
      )
    },
    ...defaultQueryConfig,
    ...options,
  })
}

// Хук для получения одного ключевого слова
export function useKeyword(
  id: number | null | undefined,
  options?: Omit<
    UseQueryOptions<KeywordResponse>,
    'queryKey' | 'queryFn' | 'enabled'
  >
) {
  return useQuery({
    queryKey: createQueryKey(QUERY_KEYS.keyword, { id }),
    queryFn: () => api.get<KeywordResponse>(`/api/v1/keywords/${id}`),
    enabled: Boolean(id),
    staleTime: 10 * 60 * 1000, // 10 минут для отдельных элементов
    ...options,
  })
}

// Хук для получения категорий ключевых слов
export function useKeywordCategories(
  options?: Omit<
    UseQueryOptions<{ categories: string[] }>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: [QUERY_KEYS.categories],
    queryFn: () =>
      api.get<{ categories: string[] }>('/api/v1/keywords/categories'),
    staleTime: 30 * 60 * 1000, // 30 минут для категорий
    ...options,
  })
}

// Хук для создания ключевого слова
export function useCreateKeyword(
  options?: Omit<
    UseMutationOptions<KeywordResponse, Error, KeywordCreate>,
    'mutationFn'
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: KeywordCreate) =>
      api.post<KeywordResponse>('/api/v1/keywords', data),
    onSuccess: (data) => {
      // Инвалидируем списки и добавляем новый элемент в кеш
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.keywords] })
      queryClient.setQueryData(
        createQueryKey(QUERY_KEYS.keyword, { id: data.id }),
        data
      )
    },
    ...options,
  })
}

// Хук для массового создания ключевых слов
export function useCreateKeywordsBulk(
  options?: Omit<
    UseMutationOptions<
      { created_keywords: KeywordResponse[] },
      Error,
      { words: string[]; default_category?: string }
    >,
    'mutationFn'
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: { words: string[]; default_category?: string }) =>
      api.post<{ created_keywords: KeywordResponse[] }>(
        '/api/v1/keywords/bulk',
        data
      ),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.keywords] })
      // Добавляем новые элементы в кеш
      data.created_keywords.forEach((keyword) => {
        queryClient.setQueryData(
          createQueryKey(QUERY_KEYS.keyword, { id: keyword.id }),
          keyword
        )
      })
    },
    ...options,
  })
}

// Хук для загрузки ключевых слов из файла
export function useUploadKeywordsFromFile(
  options?: Omit<
    UseMutationOptions<
      KeywordUploadResponse,
      Error,
      {
        file: File
        options?: {
          default_category?: string
          is_active?: boolean
          is_case_sensitive?: boolean
          is_whole_word?: boolean
        }
      }
    >,
    'mutationFn'
  >
) {
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
    }) => {
      const formData = new FormData()
      formData.append('file', file)

      if (options?.default_category?.trim()) {
        formData.append('default_category', options.default_category.trim())
      }
      if (options?.is_active !== undefined) {
        formData.append('is_active', options.is_active.toString())
      }
      if (options?.is_case_sensitive !== undefined) {
        formData.append(
          'is_case_sensitive',
          options.is_case_sensitive.toString()
        )
      }
      if (options?.is_whole_word !== undefined) {
        formData.append('is_whole_word', options.is_whole_word.toString())
      }

      return api.post<KeywordUploadResponse>(
        '/api/v1/keywords/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.keywords] })
      // Добавляем новые элементы в кеш
      data.created_keywords?.forEach((keyword) => {
        queryClient.setQueryData(
          createQueryKey(QUERY_KEYS.keyword, { id: keyword.id }),
          keyword
        )
      })
    },
    ...options,
  })
}

// Хук для обновления ключевого слова
export function useUpdateKeyword(
  options?: Omit<
    UseMutationOptions<
      KeywordResponse,
      Error,
      { keywordId: number; data: KeywordUpdate }
    >,
    'mutationFn'
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      keywordId,
      data,
    }: {
      keywordId: number
      data: KeywordUpdate
    }) => api.patch<KeywordResponse>(`/api/v1/keywords/${keywordId}`, data),
    onSuccess: (data, { keywordId }) => {
      // Обновляем кеш для конкретного элемента
      queryClient.setQueryData(
        createQueryKey(QUERY_KEYS.keyword, { id: keywordId }),
        data
      )
      // Инвалидируем списки
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.keywords] })
    },
    ...options,
  })
}

// Хук для удаления ключевого слова
export function useDeleteKeyword(
  options?: Omit<UseMutationOptions<void, Error, number>, 'mutationFn'>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (keywordId: number) =>
      api.delete(`/api/v1/keywords/${keywordId}`),
    onSuccess: (_, keywordId) => {
      // Удаляем элемент из кеша
      queryClient.removeQueries({
        queryKey: createQueryKey(QUERY_KEYS.keyword, { id: keywordId }),
      })
      // Инвалидируем списки
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.keywords] })
    },
    ...options,
  })
}

// Хук для обновления статистики ключевых слов
export function useUpdateKeywordsStats(
  options?: Omit<
    UseMutationOptions<{ message: string }, Error, void>,
    'mutationFn'
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () =>
      api.post<{ message: string }>('/api/v1/keywords/update-stats'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.keywords] })
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.totalMatches] })
    },
    ...options,
  })
}

// Хук для получения общего количества совпадений
export function useTotalMatches(
  options?: Omit<
    UseQueryOptions<{ total_matches: number }>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: [QUERY_KEYS.totalMatches],
    queryFn: () =>
      api.get<{ total_matches: number }>('/api/v1/keywords/total-matches'),
    ...defaultQueryConfig,
    ...options,
  })
}

// Хук для бесконечной прокрутки ключевых слов
export function useInfiniteKeywords(
  params?: InfiniteKeywordsParams,
  options?: Omit<
    UseInfiniteQueryOptions<PaginatedResponse<KeywordResponse>>,
    'queryKey' | 'queryFn' | 'getNextPageParam' | 'initialPageParam'
  >
) {
  const {
    active_only,
    category,
    q,
    pageSize = 20,
    order_by,
    order_dir,
  } = params || {}

  const queryParams = {
    ...(active_only !== undefined && { active_only }),
    ...(category?.trim() && { category: category.trim() }),
    ...(q?.trim() && { q: q.trim() }),
    ...(order_by?.trim() && { order_by: order_by.trim() }),
    ...(order_dir && { order_dir }),
  }

  return useInfiniteQuery({
    queryKey: createQueryKey(QUERY_KEYS.infiniteKeywords, {
      ...queryParams,
      pageSize,
    }),
    queryFn: ({ pageParam = 1 }) => {
      const searchParams = buildQueryParams({
        page: pageParam,
        size: pageSize,
        ...queryParams,
      })

      return api.get<PaginatedResponse<KeywordResponse>>(
        `/api/v1/keywords?${searchParams}`
      )
    },
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((acc, page) => acc + page.items.length, 0)
      if (loaded < (lastPage?.total || 0)) {
        return allPages.length + 1
      }
      return undefined
    },
    initialPageParam: 1,
    ...defaultQueryConfig,
    ...options,
  })
}
