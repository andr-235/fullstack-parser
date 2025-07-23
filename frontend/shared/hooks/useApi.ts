import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from '@tanstack/react-query'
import {
  apiService,
  apiUtils,
  type ApiResponse,
  type ApiError,
} from '@/shared/lib/api'
import { CACHE_CONFIG } from '@/shared/config'

// Базовые опции для запросов
const defaultQueryOptions = {
  staleTime: CACHE_CONFIG.staleTime,
  cacheTime: CACHE_CONFIG.cacheTime,
  retry: 3,
  retryDelay: (attemptIndex: number) =>
    Math.min(1000 * 2 ** attemptIndex, 30000),
}

// Хук для GET запросов
export function useApiQuery<T>(
  key: readonly unknown[],
  url: string,
  options?: Omit<
    UseQueryOptions<ApiResponse<T>, ApiError>,
    'queryKey' | 'queryFn'
  >
) {
  return useQuery({
    queryKey: key,
    queryFn: () => apiService.get<T>(url),
    ...defaultQueryOptions,
    ...options,
  })
}

// Хук для POST запросов
export function useApiMutation<T, V = any>(
  url: string,
  options?: Omit<UseMutationOptions<ApiResponse<T>, ApiError, V>, 'mutationFn'>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: V) => apiService.post<T>(url, data),
    ...options,
    onSuccess: (data, variables, context) => {
      // Инвалидируем кеш после успешной мутации
      queryClient.invalidateQueries()
      options?.onSuccess?.(data, variables, context)
    },
  })
}

// Хук для PUT запросов
export function useApiUpdate<T, V = any>(
  url: string,
  options?: Omit<UseMutationOptions<ApiResponse<T>, ApiError, V>, 'mutationFn'>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: V) => apiService.put<T>(url, data),
    ...options,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries()
      options?.onSuccess?.(data, variables, context)
    },
  })
}

// Хук для PATCH запросов
export function useApiPatch<T, V = any>(
  url: string,
  options?: Omit<UseMutationOptions<ApiResponse<T>, ApiError, V>, 'mutationFn'>
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: V) => apiService.patch<T>(url, data),
    ...options,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries()
      options?.onSuccess?.(data, variables, context)
    },
  })
}

// Хук для DELETE запросов
export function useApiDelete<T>(
  url: string,
  options?: Omit<
    UseMutationOptions<ApiResponse<T>, ApiError, void>,
    'mutationFn'
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => apiService.delete<T>(url),
    ...options,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries()
      options?.onSuccess?.(data, variables, context)
    },
  })
}

// Хук для загрузки файлов
export function useApiUpload<T>(
  url: string,
  options?: Omit<
    UseMutationOptions<
      ApiResponse<T>,
      ApiError,
      { file: File; onProgress?: (progress: number) => void }
    >,
    'mutationFn'
  >
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ file, onProgress }) =>
      apiService.upload<T>(url, file, onProgress),
    ...options,
    onSuccess: (data, variables, context) => {
      queryClient.invalidateQueries()
      options?.onSuccess?.(data, variables, context)
    },
  })
}

// Хук для оптимистичных обновлений
export function useOptimisticUpdate<T, V = any>(
  queryKey: readonly unknown[],
  url: string,
  options?: {
    updateFn?: (oldData: T | undefined, newData: V) => T
    rollbackOnError?: boolean
  }
) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: V) => apiService.put<ApiResponse<T>>(url, data),
    onMutate: async (newData) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey })

      // Сохраняем предыдущее значение
      const previousData = queryClient.getQueryData<T>(queryKey)

      // Оптимистично обновляем кеш
      if (options?.updateFn) {
        queryClient.setQueryData<T>(queryKey, (old) =>
          options.updateFn!(old, newData)
        )
      }

      return { previousData }
    },
    onError: (err, newData, context) => {
      // Откатываем изменения при ошибке
      if (options?.rollbackOnError !== false && context?.previousData) {
        queryClient.setQueryData<T>(queryKey, context.previousData)
      }
    },
    onSettled: () => {
      // Всегда инвалидируем кеш после завершения
      queryClient.invalidateQueries({ queryKey })
    },
  })
}

// Хук для бесконечной прокрутки
export function useInfiniteQuery<T>(
  key: readonly unknown[],
  url: string,
  options?: {
    pageParam?: number
  }
) {
  return useQuery({
    queryKey: key,
    queryFn: ({ pageParam = 1 }) => {
      const urlWithParams = apiUtils.createUrl(url, { page: pageParam })
      return apiService.get<T>(urlWithParams)
    },
    ...defaultQueryOptions,
  })
}

// Утилиты для работы с кешем
export const queryUtils = {
  // Инвалидация конкретного запроса
  invalidateQuery: (queryKey: readonly unknown[]) => {
    const queryClient = useQueryClient()
    return queryClient.invalidateQueries({ queryKey })
  },

  // Удаление запроса из кеша
  removeQuery: (queryKey: readonly unknown[]) => {
    const queryClient = useQueryClient()
    return queryClient.removeQueries({ queryKey })
  },

  // Обновление данных в кеше
  setQueryData: <T>(queryKey: readonly unknown[], data: T) => {
    const queryClient = useQueryClient()
    return queryClient.setQueryData<T>(queryKey, data)
  },

  // Получение данных из кеша
  getQueryData: <T>(queryKey: readonly unknown[]) => {
    const queryClient = useQueryClient()
    return queryClient.getQueryData<T>(queryKey)
  },

  // Предварительная загрузка данных
  prefetchQuery: <T>(queryKey: readonly unknown[], url: string) => {
    const queryClient = useQueryClient()
    return queryClient.prefetchQuery({
      queryKey,
      queryFn: () => apiService.get<T>(url),
      ...defaultQueryOptions,
    })
  },
}
