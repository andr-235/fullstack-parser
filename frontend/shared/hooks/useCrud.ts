/**
 * Базовые CRUD хуки с стандартизированной обработкой ошибок и loading состояний
 */

import { useApiQuery, useApiMutation } from './useApi'
import { useToast } from './use-toast'
import type { UseQueryOptions, UseMutationOptions } from '@tanstack/react-query'

// Стандартизированные типы для CRUD операций
export interface CrudOptions<TData = unknown, TVariables = unknown> {
  onSuccess?: (data: TData) => void
  onError?: (error: Error) => void
  successMessage?: string
  errorMessage?: string
}

export interface CreateOptions<TData = unknown, TVariables = unknown> extends CrudOptions<TData, TVariables> {}
export interface ReadOptions<TData = unknown> {
  enabled?: boolean
  staleTime?: number
  refetchOnWindowFocus?: boolean
  refetchOnMount?: boolean
  retry?: boolean | number
  retryDelay?: number
  onSuccess?: (data: TData) => void
  onError?: (error: Error) => void
}
export interface UpdateOptions<TData = unknown, TVariables = unknown> extends CrudOptions<TData, TVariables> {}
export interface DeleteOptions<TData = unknown> extends CrudOptions<TData, void> {}

// Хук для создания сущности
export function useCreate<TData = unknown, TVariables = unknown>(
  endpoint: string,
  options: CreateOptions<TData, TVariables> = {}
) {
  const { toast } = useToast()

  const mutation = useApiMutation<TData, TVariables>({
    endpoint,
    method: 'POST',
    onSuccess: (data) => {
      if (options.successMessage) {
        toast({
          title: 'Успешно',
          description: options.successMessage,
        })
      }
      options.onSuccess?.(data)
    },
    onError: (error) => {
      const message = options.errorMessage || `Ошибка при создании: ${error.message}`
      toast({
        title: 'Ошибка',
        description: message,
        variant: 'destructive',
      })
      options.onError?.(error)
    },
  })

  return {
    create: mutation.mutate,
    createAsync: mutation.mutateAsync,
    isCreating: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  }
}

// Хук для чтения списка сущностей
export function useReadList<TData = unknown>(
  endpoint: string,
  params?: Record<string, unknown>,
  options: ReadOptions<TData> = {}
) {
  const queryOptions: any = {
    endpoint,
    params: params || {},
    queryKey: [endpoint, JSON.stringify(params || {})],
  }

  if (options.enabled !== undefined) queryOptions.enabled = options.enabled
  if (options.staleTime !== undefined) queryOptions.staleTime = options.staleTime
  if (options.refetchOnWindowFocus !== undefined) queryOptions.refetchOnWindowFocus = options.refetchOnWindowFocus
  if (options.refetchOnMount !== undefined) queryOptions.refetchOnMount = options.refetchOnMount
  if (options.retry !== undefined) queryOptions.retry = options.retry
  if (options.retryDelay !== undefined) queryOptions.retryDelay = options.retryDelay

  const query = useApiQuery<TData>(queryOptions)

  // Вызываем колбэки вручную
  if (options.onSuccess && query.data) {
    options.onSuccess(query.data)
  }
  if (options.onError && query.error) {
    options.onError(query.error)
  }

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    isRefetching: query.isRefetching,
  }
}

// Хук для чтения одной сущности
export function useReadOne<TData = unknown>(
  endpoint: string,
  id?: string | number,
  options: ReadOptions<TData> = {}
) {
  const fullEndpoint = id ? `${endpoint}/${id}` : endpoint

  const queryOptions: any = {
    endpoint: fullEndpoint,
    queryKey: [fullEndpoint],
  }

  if (options.enabled !== undefined) queryOptions.enabled = options.enabled
  if (options.staleTime !== undefined) queryOptions.staleTime = options.staleTime
  if (options.refetchOnWindowFocus !== undefined) queryOptions.refetchOnWindowFocus = options.refetchOnWindowFocus
  if (options.refetchOnMount !== undefined) queryOptions.refetchOnMount = options.refetchOnMount
  if (options.retry !== undefined) queryOptions.retry = options.retry
  if (options.retryDelay !== undefined) queryOptions.retryDelay = options.retryDelay

  const query = useApiQuery<TData>(queryOptions)

  // Вызываем колбэки вручную
  if (options.onSuccess && query.data) {
    options.onSuccess(query.data)
  }
  if (options.onError && query.error) {
    options.onError(query.error)
  }

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    isRefetching: query.isRefetching,
  }
}

// Хук для обновления сущности
export function useUpdate<TData = unknown, TVariables = unknown>(
  endpoint: string,
  options: UpdateOptions<TData, TVariables> = {}
) {
  const { toast } = useToast()

  const mutation = useApiMutation<TData, TVariables>({
    endpoint,
    method: 'PATCH',
    onSuccess: (data) => {
      if (options.successMessage) {
        toast({
          title: 'Успешно',
          description: options.successMessage,
        })
      }
      options.onSuccess?.(data)
    },
    onError: (error) => {
      const message = options.errorMessage || `Ошибка при обновлении: ${error.message}`
      toast({
        title: 'Ошибка',
        description: message,
        variant: 'destructive',
      })
      options.onError?.(error)
    },
  })

  return {
    update: mutation.mutate,
    updateAsync: mutation.mutateAsync,
    isUpdating: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  }
}

// Хук для удаления сущности
export function useDelete<TData = unknown>(
  endpoint: string,
  options: DeleteOptions<TData> = {}
) {
  const { toast } = useToast()

  const mutation = useApiMutation<TData, void>({
    endpoint,
    method: 'DELETE',
    onSuccess: (data) => {
      if (options.successMessage) {
        toast({
          title: 'Успешно',
          description: options.successMessage,
        })
      }
      options.onSuccess?.(data)
    },
    onError: (error) => {
      const message = options.errorMessage || `Ошибка при удалении: ${error.message}`
      toast({
        title: 'Ошибка',
        description: message,
        variant: 'destructive',
      })
      options.onError?.(error)
    },
  })

  return {
    delete: mutation.mutate,
    deleteAsync: mutation.mutateAsync,
    isDeleting: mutation.isPending,
    isSuccess: mutation.isSuccess,
    isError: mutation.isError,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  }
}

// Универсальный CRUD хук для сущности
export function useCrud<TData = unknown, TCreate = unknown, TUpdate = unknown>(
  baseEndpoint: string
) {
  return {
    // Create
    create: useCreate<TData, TCreate>(baseEndpoint),

    // Read list
    readList: (params?: Record<string, unknown>, options?: ReadOptions<TData[]>) =>
      useReadList<TData[]>(baseEndpoint, params, options),

    // Read one
    readOne: (id: string | number, options?: ReadOptions<TData>) =>
      useReadOne<TData>(baseEndpoint, id, options),

    // Update
    update: (id: string | number) =>
      useUpdate<TData, TUpdate>(`${baseEndpoint}/${id}`),

    // Delete
    delete: (id: string | number) =>
      useDelete<TData>(`${baseEndpoint}/${id}`),
  }
}