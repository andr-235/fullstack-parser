import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { api } from '@/shared/lib/api'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  PaginatedResponse,
  PaginationParams,
} from '@/types/api'

// Параметры для получения групп
export interface UseGroupsParams extends PaginationParams {
  active_only?: boolean
  search?: string
}

// Параметры для бесконечной прокрутки групп
export interface UseInfiniteGroupsParams {
  active_only?: boolean
  search?: string
  pageSize?: number
}

// Параметры для получения одной группы
export interface UseGroupParams {
  groupId: number
  enabled?: boolean
}

// Параметры для статистики группы
export interface UseGroupStatsParams {
  groupId: number
  enabled?: boolean
}

// Хук для получения списка групп
export function useGroups(params?: UseGroupsParams) {
  const { page = 1, size = 20, active_only, search } = params || {}

  return useQuery({
    queryKey: ['groups', { page, size, active_only, search }],
    queryFn: () => {
      const searchParams = new URLSearchParams()
      if (page) searchParams.append('page', page.toString())
      if (size) searchParams.append('size', size.toString())
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

// Хук для бесконечной прокрутки групп
export function useInfiniteGroups(params?: UseInfiniteGroupsParams) {
  const { active_only, search, pageSize = 20 } = params || {}

  return useInfiniteQuery({
    queryKey: ['infinite-groups', { active_only, search, pageSize }],
    queryFn: ({ pageParam = 1 }) => {
      const searchParams = new URLSearchParams()
      searchParams.append('page', pageParam.toString())
      searchParams.append('size', pageSize.toString())
      if (active_only !== undefined)
        searchParams.append('active_only', active_only.toString())
      if (search) searchParams.append('search', search)

      return api.get<PaginatedResponse<VKGroupResponse>>(
        `/groups?${searchParams.toString()}`
      )
    },
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce(
        (acc, page) => acc + page.data.items.length,
        0
      )
      if (loaded < (lastPage?.data.total || 0)) {
        return allPages.length + 1
      }
      return undefined
    },
    initialPageParam: 1,
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для получения одной группы
export function useGroup({ groupId, enabled = true }: UseGroupParams) {
  return useQuery({
    queryKey: ['group', groupId],
    queryFn: () => api.get<VKGroupResponse>(`/groups/${groupId}`),
    enabled: enabled && !!groupId,
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
export function useGroupStats({
  groupId,
  enabled = true,
}: UseGroupStatsParams) {
  return useQuery({
    queryKey: ['group-stats', groupId],
    queryFn: () => api.get<any>(`/groups/${groupId}/stats`),
    enabled: enabled && !!groupId,
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для обновления информации о группе
export function useRefreshGroupInfo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (groupId: number) =>
      api.post<VKGroupResponse>(`/groups/${groupId}/refresh`),
    onSuccess: (_, groupId) => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      queryClient.invalidateQueries({ queryKey: ['group', groupId] })
      queryClient.invalidateQueries({ queryKey: ['group-stats', groupId] })
    },
  })
}
