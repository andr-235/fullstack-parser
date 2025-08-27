import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from '@tanstack/react-query'
import { api, type ApiResponse, type ApiError } from '@/shared/lib/api'

// Хук для API запросов
export function useApiQuery<T>(
  key: readonly unknown[],
  url: string,
  options?: Omit<UseQueryOptions<T, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: key,
    queryFn: () => api.get<T>(url),
    ...options,
  })
}

// Хук для API мутаций
export function useApiMutation<T, V = any>(
  url: string,
  options?: Omit<UseMutationOptions<T, ApiError, V>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: (data: V) => api.post<T>(url, data),
    ...options,
  })
}

// Хук для API обновлений (PUT)
export function useApiUpdate<T, V = any>(
  url: string,
  options?: Omit<UseMutationOptions<T, ApiError, V>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: (data: V) => api.put<T>(url, data),
    ...options,
  })
}

// Хук для API обновлений (PATCH)
export function useApiPatch<T, V = any>(
  url: string,
  options?: Omit<UseMutationOptions<T, ApiError, V>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: (data: V) => api.patch<T>(url, data),
    ...options,
  })
}

// Хук для API удалений
export function useApiDelete<T>(
  url: string,
  options?: Omit<UseMutationOptions<T, ApiError, void>, 'mutationFn'>
) {
  return useMutation({
    mutationFn: () => api.delete<T>(url),
    ...options,
  })
}

// Хук для загрузки файлов
export function useApiUpload<T>(
  url: string,
  options?: Omit<
    UseMutationOptions<
      T,
      ApiError,
      { file: File; onProgress?: (progress: number) => void }
    >,
    'mutationFn'
  >
) {
  return useMutation({
    mutationFn: ({ file, onProgress }) => {
      const formData = new FormData()
      formData.append('file', file)

      return api.post<T>(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress(progress)
          }
        },
      })
    },
    ...options,
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
    mutationFn: (data: V) => api.patch<T>(url, data),
    onMutate: async (newData) => {
      // Отменяем исходящие запросы
      await queryClient.cancelQueries({ queryKey })

      // Сохраняем предыдущее значение
      const previousData = queryClient.getQueryData<T>(queryKey)

      // Оптимистично обновляем
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
      // Всегда инвалидируем кеш
      queryClient.invalidateQueries({ queryKey })
    },
  })
}

// Хук для бесконечных запросов
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
      const urlWithPage = url.includes('?')
        ? `${url}&page=${pageParam}`
        : `${url}?page=${pageParam}`
      return api.get<T>(urlWithPage)
    },
    ...options,
  })
}
