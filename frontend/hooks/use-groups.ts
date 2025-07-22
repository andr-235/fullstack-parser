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
      // Инвалидируем список групп
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
      // Инвалидируем конкретную группу и список групп
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
      // Инвалидируем список групп
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
