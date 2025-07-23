import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, createQueryKey } from '@/lib/api'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  PaginationParams,
} from '@/types/api'

/**
 * Хук для получения списка групп
 */
export function useGroups(params?: { active_only?: boolean; search?: string }) {
  return useQuery({
    queryKey: createQueryKey.groups(params),
    queryFn: () => api.getGroups(params),
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

/**
 * Хук для получения конкретной группы
 */
export function useGroup(groupId: number) {
  return useQuery({
    queryKey: createQueryKey.group(groupId),
    queryFn: () => api.getGroup(groupId),
    enabled: !!groupId,
  })
}

/**
 * Хук для создания группы
 */
export function useCreateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: VKGroupCreate) => api.createGroup(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

/**
 * Хук для обновления группы
 */
export function useUpdateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ groupId, data }: { groupId: number; data: VKGroupUpdate }) =>
      api.updateGroup(groupId, data),
    onSuccess: (_, { groupId }) => {
      queryClient.invalidateQueries({ queryKey: ['groups', groupId] })
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

/**
 * Хук для удаления группы
 */
export function useDeleteGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (groupId: number) => api.deleteGroup(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}

/**
 * Хук для получения статистики группы
 */
export function useGroupStats(groupId: number) {
  return useQuery({
    queryKey: createQueryKey.groupStats(groupId),
    queryFn: () => api.getGroupStats(groupId),
    enabled: !!groupId,
    staleTime: 2 * 60 * 1000, // 2 минуты
  })
}

/**
 * Хук для загрузки групп из файла
 */
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
    }) => api.uploadGroupsFromFile(file, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
