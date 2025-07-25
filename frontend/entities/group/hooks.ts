import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  PaginationParams,
  PaginatedResponse,
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

// Хук для загрузки групп из файла
export function useUploadGroupsFromFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      file,
      options,
    }: {
      file: File
      options?: {
        is_active?: boolean
        max_posts_to_check?: number
      }
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

      return api.post<any>('/groups/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
