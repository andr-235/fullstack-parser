import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type {
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
  PaginatedResponse,
  PaginationParams,
} from '@/types/api'

// Параметры для бесконечной прокрутки ключевых слов
export type InfiniteKeywordsParams = Omit<PaginationParams, 'page' | 'skip'> & {
  page?: number
  size?: number
  active_only?: boolean
  category?: string
  q?: string
  pageSize?: number
  order_by?: string
  order_dir?: 'asc' | 'desc'
}

// Хук для получения списка ключевых слов
export function useKeywords(
  params?: PaginationParams & {
    active_only?: boolean
    category?: string
    q?: string
  }
) {
  const { page = 1, size = 20, active_only, category, q } = params || {}

  return useQuery({
    queryKey: ['keywords', { page, size, active_only, category, q }],
    queryFn: () => {
      const searchParams = new URLSearchParams()
      if (page) searchParams.append('page', page.toString())
      if (size) searchParams.append('size', size.toString())
      if (active_only !== undefined)
        searchParams.append('active_only', active_only.toString())
      if (category) searchParams.append('category', category)
      if (q) searchParams.append('q', q)

      return api.get<PaginatedResponse<KeywordResponse>>(
        `/keywords?${searchParams.toString()}`
      )
    },
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для получения одного ключевого слова
export function useKeyword(keywordId: number) {
  return useQuery({
    queryKey: ['keyword', keywordId],
    queryFn: () => api.get<KeywordResponse>(`/keywords/${keywordId}`),
    enabled: !!keywordId,
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

// Хук для получения категорий ключевых слов
export function useKeywordCategories() {
  return useQuery({
    queryKey: ['keyword-categories'],
    queryFn: () => api.get<string[]>('/keywords/categories'),
    staleTime: 30 * 60 * 1000, // 30 минут
  })
}

// Хук для создания ключевого слова
export function useCreateKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: KeywordCreate) =>
      api.post<KeywordResponse>('/keywords', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

// Хук для массового создания ключевых слов
export function useCreateKeywordsBulk() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: { words: string[]; category?: string }) =>
      api.post<KeywordResponse[]>('/keywords/bulk', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

// Хук для загрузки ключевых слов из файла
export function useUploadKeywordsFromFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      file,
      options,
    }: {
      file: File
      options?: {
        category?: string
        is_active?: boolean
      }
    }) => {
      const formData = new FormData()
      formData.append('file', file)
      if (options?.category) formData.append('category', options.category)
      if (options?.is_active !== undefined)
        formData.append('is_active', options.is_active.toString())

      return api.post<any>('/keywords/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

// Хук для обновления ключевого слова
export function useUpdateKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: KeywordUpdate }) =>
      api.patch<KeywordResponse>(`/keywords/${id}`, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      queryClient.invalidateQueries({ queryKey: ['keyword', id] })
    },
  })
}

// Хук для удаления ключевого слова
export function useDeleteKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => api.delete(`/keywords/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

// Хук для обновления статистики ключевых слов
export function useUpdateKeywordsStats() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.post('/keywords/update-stats'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

// Хук для получения общего количества совпадений
export function useTotalMatches() {
  return useQuery({
    queryKey: ['total-matches'],
    queryFn: () => api.get<number>('/keywords/total-matches'),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для бесконечной прокрутки ключевых слов
export function useInfiniteKeywords(params?: InfiniteKeywordsParams) {
  const {
    active_only,
    category,
    q,
    pageSize = 20,
    order_by,
    order_dir,
  } = params || {}

  return useInfiniteQuery({
    queryKey: [
      'infinite-keywords',
      { active_only, category, q, pageSize, order_by, order_dir },
    ],
    queryFn: ({ pageParam = 1 }) => {
      const searchParams = new URLSearchParams()
      searchParams.append('page', pageParam.toString())
      searchParams.append('size', pageSize.toString())
      if (active_only !== undefined)
        searchParams.append('active_only', active_only.toString())
      if (category) searchParams.append('category', category)
      if (q) searchParams.append('q', q)
      if (order_by) searchParams.append('order_by', order_by)
      if (order_dir) searchParams.append('order_dir', order_dir)

      return api.get<PaginatedResponse<KeywordResponse>>(
        `/keywords?${searchParams.toString()}`
      )
    },
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce(
        (acc, page) => acc + page.data.items.length,
        0
      )
      if (loaded < (lastPage?.data.total || 0)) {
        return allPages.length + 1
      }
      return undefined
    },
    initialPageParam: 1,
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}
