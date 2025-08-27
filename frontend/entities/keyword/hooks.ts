import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { apiService, createQueryKey } from '@/shared/lib/api-compat'
import { api } from '@/shared/lib/api'
import type {
  KeywordResponse,
  KeywordCreate,
  KeywordUpdate,
  PaginationParams,
  KeywordUploadResponse,
} from '@/shared/types'

/**
 * Хук для получения списка ключевых слов
 */
export function useKeywords(
  params?: PaginationParams & {
    active_only?: boolean
    category?: string | undefined
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
 * Хук для загрузки ключевых слов из файла с отслеживанием прогресса
 */
export function useUploadKeywordsWithProgress() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      file,
      options,
      onProgress,
    }: {
      file: File
      options?: {
        default_category?: string
        is_active?: boolean
        is_case_sensitive?: boolean
        is_whole_word?: boolean
      }
      onProgress?: (progress: {
        status: string
        progress: number
        current_keyword: string
        total_keywords: number
        processed_keywords: number
        created: number
        skipped: number
        errors: string[]
      }) => void
    }) => {
      return new Promise<KeywordUploadResponse>((resolve, reject) => {
        const formData = new FormData()
        formData.append('file', file)
        if (options?.default_category && options.default_category.trim())
          formData.append('default_category', options.default_category)
        if (options?.is_active !== undefined)
          formData.append('is_active', options.is_active.toString())
        if (options?.is_case_sensitive !== undefined)
          formData.append(
            'is_case_sensitive',
            options.is_case_sensitive.toString()
          )
        if (options?.is_whole_word !== undefined)
          formData.append('is_whole_word', options.is_whole_word.toString())

        // Симулируем прогресс для ключевых слов
        let progress = 0
        const progressInterval = setInterval(() => {
          progress += Math.random() * 10
          if (progress > 90) progress = 90

          onProgress?.({
            status: 'processing',
            progress: Math.round(progress),
            current_keyword: `Обработка ключевых слов...`,
            total_keywords: 0,
            processed_keywords: 0,
            created: 0,
            skipped: 0,
            errors: [],
          })
        }, 200)

        api
          .post<KeywordUploadResponse>('/keywords/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          })
          .then((response) => {
            clearInterval(progressInterval)

            // Проверяем, что response существует и содержит нужные поля
            if (!response || typeof response !== 'object') {
              throw new Error('Неверный формат ответа от сервера')
            }

            // Финальный прогресс
            onProgress?.({
              status: 'completed',
              progress: 100,
              current_keyword: '',
              total_keywords: response.total_processed || 0,
              processed_keywords: response.total_processed || 0,
              created: response.created || 0,
              skipped: response.skipped || 0,
              errors: response.errors || [],
            })

            resolve(response)
          })
          .catch((error) => {
            clearInterval(progressInterval)
            reject(error)
          })
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
      queryClient.invalidateQueries({ queryKey: ['keywords', 'categories'] })
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

/**
 * Хук для обновления статистики ключевых слов
 */
export function useUpdateKeywordsStats() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => api.post<{ message: string }>('/keywords/update-stats'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] })
    },
  })
}

/**
 * Хук для получения общего количества совпадений
 */
export function useTotalMatches() {
  return useQuery({
    queryKey: ['keywords', 'total-matches'],
    queryFn: () =>
      api.get<{ total_matches: number }>('/keywords/total-matches'),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}
