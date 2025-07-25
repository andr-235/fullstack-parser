import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { apiService } from '@/shared/lib/api-compat'
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

      return apiService.getGroups({ page, size, active_only, search })
    },
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для бесконечной прокрутки групп
export function useInfiniteGroups(params?: UseInfiniteGroupsParams) {
  const { active_only, search, pageSize = 20 } = params || {}

  return useInfiniteQuery({
    queryKey: ['groups', active_only, search],
    queryFn: ({ pageParam = 1 }) =>
      apiService.getGroups({
        page: pageParam,
        size: 20,
        active_only,
        search,
      }),
    getNextPageParam: (lastPage) => {
      const currentPage = lastPage?.page || 1
      const total = lastPage?.total || 0
      const size = lastPage?.size || 20
      const hasNextPage = currentPage * size < total
      return hasNextPage ? currentPage + 1 : undefined
    },
    initialPageParam: 1,
  })
}

// Хук для получения одной группы
export function useGroup({ groupId, enabled = true }: UseGroupParams) {
  return useQuery({
    queryKey: ['group', groupId],
    queryFn: () => apiService.getGroup(groupId),
    enabled: enabled && !!groupId,
    staleTime: 10 * 60 * 1000, // 10 минут
  })
}

// Хук для создания группы
export function useCreateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: VKGroupCreate) => apiService.createGroup(data),
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
      apiService.updateGroup(groupId, data),
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
    mutationFn: (groupId: number) => apiService.deleteGroup(groupId),
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
    queryFn: () => apiService.getGroupStats(groupId),
    enabled: enabled && !!groupId,
    staleTime: 5 * 60 * 1000, // 5 минут
  })
}

// Хук для обновления информации о группе
export function useRefreshGroupInfo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (groupId: number) => apiService.refreshGroupInfo(groupId),
    onSuccess: (_, groupId) => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
      queryClient.invalidateQueries({ queryKey: ['group', groupId] })
      queryClient.invalidateQueries({ queryKey: ['group-stats', groupId] })
    },
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
    }) => apiService.uploadGroupsFromFile(file, options),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
