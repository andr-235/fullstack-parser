import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { apiService, createQueryKey } from '@/shared/lib/api-compat'
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
    queryFn: () => apiService.getKeywords(params),
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

/**
 * Хук для бесконечной загрузки ключевых слов
 */
export function useInfiniteKeywords(
  params?: Omit<PaginationParams, 'page'> & {
    active_only?: boolean
    category?: string
    q?: string
  }
) {
  return useInfiniteQuery({
    queryKey: createQueryKey.keywords(params),
    queryFn: ({ pageParam = 1 }) =>
      apiService.getKeywords({ ...params, page: pageParam }),
    getNextPageParam: (lastPage: any) => {
      if (lastPage.next_page) {
        return lastPage.next_page
      }
      return undefined
    },
    initialPageParam: 1,
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

/**
 * Хук для получения конкретного ключевого слова
 */
export function useKeyword(keywordId: number) {
  return useQuery({
    queryKey: createQueryKey.keyword(keywordId),
    queryFn: () => apiService.getKeyword(keywordId),
    enabled: !!keywordId,
  })
}

/**
 * Хук для получения категорий ключевых слов
 */
export function useKeywordCategories() {
  return useQuery({
    queryKey: createQueryKey.keywordCategories(),
    queryFn: () => apiService.getKeywordCategories(),
    staleTime: 30 * 60 * 1000, // 30 минут
  })
}

/**
 * Хук для создания ключевого слова
 */
export function useCreateKeyword() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: KeywordCreate) => apiService.createKeyword(data),
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
    mutationFn: (data: KeywordCreate[]) => apiService.createKeywordsBulk(data),
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
    }) => apiService.updateKeyword(keywordId, data),
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
    mutationFn: (keywordId: number) => apiService.deleteKeyword(keywordId),
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
    }) => apiService.uploadKeywordsFromFile(file, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      queryClient.invalidateQueries({ queryKey: ['keywords', 'categories'] })
    },
  })
}
