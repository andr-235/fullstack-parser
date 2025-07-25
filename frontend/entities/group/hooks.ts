import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  PaginationParams,
  PaginatedResponse,
  VKGroupUploadResponse,
} from '@/types/api'

// Хук для получения групп
export function useGroups(
  params?: { active_only?: boolean; search?: string } & PaginationParams
) {
  const { page = 1, size = 20, active_only, search } = params || {}

  return useQuery({
    queryKey: ['groups', { page, size, active_only, search }],
    queryFn: () => {
      const searchParams = new URLSearchParams()
      searchParams.append('page', page.toString())
      searchParams.append('size', size.toString())
      if (active_only !== undefined)
        searchParams.append('active_only', active_only.toString())
      if (search) searchParams.append('search', search)

      return api.get<PaginatedResponse<VKGroupResponse>>(
        `/groups?${searchParams.toString()}`
      )
    },
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для получения одной группы
export function useGroup(groupId: number) {
  return useQuery({
    queryKey: ['group', groupId],
    queryFn: () => api.get<VKGroupResponse>(`/groups/${groupId}`),
    enabled: !!groupId,
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

// Хук для создания группы
export function useCreateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: VKGroupCreate) =>
      api.post<VKGroupResponse>('/groups', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

// Хук для обновления группы
export function useUpdateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ groupId, data }: { groupId: number; data: VKGroupUpdate }) =>
      api.patch<VKGroupResponse>(`/groups/${groupId}`, data),
    onSuccess: (_, { groupId }) => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      queryClient.invalidateQueries({ queryKey: ['group', groupId] })
    },
  })
}

// Хук для удаления группы
export function useDeleteGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (groupId: number) => api.delete(`/groups/${groupId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

// Хук для получения статистики группы
export function useGroupStats(groupId: number) {
  return useQuery({
    queryKey: ['group-stats', groupId],
    queryFn: () => api.get<any>(`/groups/${groupId}/stats`),
    enabled: !!groupId,
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для загрузки групп из файла с отслеживанием прогресса
export function useUploadGroupsWithProgress() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      file,
      options,
      onProgress,
    }: {
      file: File
      options?: {
        is_active?: boolean
        max_posts_to_check?: number
      }
      onProgress?: (progress: {
        status: string
        progress: number
        current_group: string
        total_groups: number
        processed_groups: number
        created: number
        skipped: number
        errors: string[]
      }) => void
    }) => {
      return new Promise<VKGroupUploadResponse>((resolve, reject) => {
        const formData = new FormData()
        formData.append('file', file)
        if (options?.is_active !== undefined)
          formData.append('is_active', options.is_active.toString())
        if (options?.max_posts_to_check)
          formData.append(
            'max_posts_to_check',
            options.max_posts_to_check.toString()
          )

        // Отправляем файл и получаем upload_id
        fetch('/api/v1/groups/upload-with-progress/', {
          method: 'POST',
          body: formData,
        })
          .then((response) => response.json())
          .then((data: { upload_id: string; status: string }) => {
            const uploadId = data.upload_id

            // Функция для проверки прогресса
            const checkProgress = () => {
              fetch(`/api/v1/groups/upload-progress/${uploadId}`)
                .then((response) => {
                  if (response.ok) {
                    return response.json()
                  } else if (response.status === 404) {
                    throw new Error('Прогресс загрузки не найден')
                  } else {
                    throw new Error('Ошибка получения прогресса')
                  }
                })
                .then((progressData) => {
                  onProgress?.(progressData)

                  if (progressData.status === 'completed') {
                    // Загрузка завершена
                    const result: VKGroupUploadResponse = {
                      status: 'success',
                      message: 'Загрузка завершена',
                      total_processed: progressData.total_groups,
                      created: progressData.created,
                      skipped: progressData.skipped,
                      errors: progressData.errors,
                      created_groups: [],
                    }
                    resolve(result)
                  } else if (progressData.status === 'error') {
                    reject(new Error(progressData.errors.join(', ')))
                  } else {
                    // Продолжаем проверять прогресс
                    setTimeout(checkProgress, 500) // Уменьшаем интервал до 500мс
                  }
                })
                .catch((error) => {
                  reject(error)
                })
            }

            // Начинаем проверку прогресса
            checkProgress()
          })
          .catch(reject)
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

// Хук для загрузки групп из файла
export function useUploadGroupsFromFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      file,
      options,
      onProgress,
    }: {
      file: File
      options?: {
        is_active?: boolean
        max_posts_to_check?: number
      }
      onProgress?: (progress: number) => void
    }) => {
      const formData = new FormData()
      formData.append('file', file)
      if (options?.is_active !== undefined)
        formData.append('is_active', options.is_active.toString())
      if (options?.max_posts_to_check)
        formData.append(
          'max_posts_to_check',
          options.max_posts_to_check.toString()
        )

      const res = await api
        .post<VKGroupUploadResponse>('/groups/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent_1) => {
            if (onProgress && progressEvent_1.total) {
              const progress_1 = Math.round(
                (progressEvent_1.loaded * 100) / progressEvent_1.total
              )
              onProgress(progress_1)
            }
          },
        })
        .then((response) => response.data)

      return res
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
