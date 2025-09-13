import {
  useQuery,
  useMutation,
  type UseQueryOptions,
  type UseMutationOptions,
} from '@tanstack/react-query'
import { httpClient } from '@/shared/lib'

// Типы для API хуков
type ApiQueryOptions<TData = unknown> = Omit<
  UseQueryOptions<TData, Error, TData, string[]>,
  'queryFn'
> & {
  endpoint: string
  params?: Record<string, unknown>
}

type ApiMutationOptions<TData = unknown, TVariables = unknown> = Omit<
  UseMutationOptions<TData, Error, TVariables, unknown>,
  'mutationFn'
> & {
  endpoint: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
}

// Хук для GET запросов
export function useApiQuery<TData = unknown>({
  endpoint,
  params,
  ...options
}: ApiQueryOptions<TData>) {
  return useQuery({
    ...options,
    queryKey: [endpoint, JSON.stringify(params || {})],
    queryFn: async () => {
      return await httpClient.get<TData>(endpoint, params)
    },
  })
}

// Хук для мутаций (POST, PUT, DELETE)
export function useApiMutation<TData = unknown, TVariables = unknown>({
  endpoint,
  method = 'POST',
  ...options
}: ApiMutationOptions<TData, TVariables>) {
  return useMutation({
    mutationFn: async (variables: TVariables) => {
      switch (method) {
        case 'POST':
          return await httpClient.post<TData>(endpoint, variables)
        case 'PUT':
          return await httpClient.put<TData>(endpoint, variables)
        case 'PATCH':
          return await httpClient.patch<TData>(endpoint, variables)
        case 'DELETE':
          return await httpClient.delete<TData>(endpoint)
        default:
          throw new Error(`Unsupported method: ${method}`)
      }
    },
    ...options,
  })
}

// Хук для загрузки файлов
export function useFileUpload<TData = unknown>({
  endpoint,
  ...options
}: Omit<ApiMutationOptions<TData, FormData>, 'method'>) {
  return useMutation({
    mutationFn: async (formData: FormData) => {
      // Для загрузки файлов используем fetch напрямую
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`)
      }
      
      return await response.json() as TData
    },
    ...options,
  })
}
