import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query'
import { api, createQueryKey } from '@/shared/lib/api'
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  PaginationParams,
} from '@/types/api'
import type {
  UseGroupsParams,
  UseInfiniteGroupsParams,
  UseGroupParams,
  UseGroupStatsParams,
  CreateGroupParams,
  UpdateGroupParams,
  DeleteGroupParams,
  RefreshGroupParams,
  GroupsCacheConfig,
} from '../types'

// Константы для оптимизации
const GROUPS_STALE_TIME = 5 * 60 * 1000 // 5 минут
const GROUP_STATS_STALE_TIME = 2 * 60 * 1000 // 2 минуты
const DEFAULT_PAGE_SIZE = 50

/**
 * Хук для получения списка групп
 */
export function useGroups(params?: UseGroupsParams) {
  return useQuery({
    queryKey: createQueryKey.groups(params),
    queryFn: () => api.getGroups(params),
    staleTime: GROUPS_STALE_TIME,
    gcTime: 10 * 60 * 1000, // 10 минут для garbage collection
  })
}

/**
 * Хук для бесконечной загрузки групп (infinite scroll)
 */
export function useInfiniteGroups(params?: UseInfiniteGroupsParams) {
  const pageSize = params?.pageSize || DEFAULT_PAGE_SIZE

  return useInfiniteQuery({
    queryKey: createQueryKey.groups({ ...params, pageSize }),
    queryFn: async ({ pageParam = 1 }) => {
      const { pageSize, ...rest } = params ?? {}
      const res = await api.getGroups({
        ...rest,
        page: pageParam,
        size: pageSize,
      } as any)
      return res
    },
    getNextPageParam: (lastPage, allPages) => {
      const loaded = allPages.reduce((acc, page) => acc + page.items.length, 0)
      if (loaded < (lastPage?.total || 0)) {
        return allPages.length + 1
      }
      return undefined
    },
    initialPageParam: 1,
    staleTime: GROUPS_STALE_TIME,
    gcTime: 10 * 60 * 1000,
  })
}

/**
 * Хук для получения конкретной группы
 */
export function useGroup({ groupId, enabled = true }: UseGroupParams) {
  return useQuery({
    queryKey: createQueryKey.group(groupId),
    queryFn: () => api.getGroup(groupId),
    enabled: !!groupId,
    staleTime: GROUPS_STALE_TIME,
    gcTime: 10 * 60 * 1000,
  })
}

/**
 * Хук для создания группы
 */
export function useCreateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateGroupParams) => api.createGroup(data),
    onSuccess: () => {
      // Инвалидируем список групп
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
    onError: (error) => {
      console.error('Error creating group:', error)
    },
  })
}

/**
 * Хук для обновления группы
 */
export function useUpdateGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ groupId, data }: UpdateGroupParams) =>
      api.updateGroup(groupId, data),
    onSuccess: (_, { groupId }) => {
      // Инвалидируем конкретную группу и список групп
      queryClient.invalidateQueries({ queryKey: ['groups', groupId] })
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
    onError: (error) => {
      console.error('Error updating group:', error)
    },
  })
}

/**
 * Хук для удаления группы
 */
export function useDeleteGroup() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ groupId }: DeleteGroupParams) => api.deleteGroup(groupId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
    onError: (error) => {
      console.error('Error deleting group:', error)
    },
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

/**
 * Хук для получения статистики группы
 */
export function useGroupStats({
  groupId,
  enabled = true,
}: UseGroupStatsParams) {
  return useQuery({
    queryKey: createQueryKey.groupStats(groupId),
    queryFn: () => api.getGroupStats(groupId),
    enabled: !!groupId,
    staleTime: GROUP_STATS_STALE_TIME,
    gcTime: 5 * 60 * 1000,
  })
}

/**
 * Хук для обновления информации о группе из VK API
 */
export function useRefreshGroupInfo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ groupId }: RefreshGroupParams) =>
      api.refreshGroupInfo(groupId),
    onSuccess: (_, { groupId }) => {
      // Инвалидируем конкретную группу и список групп
      queryClient.invalidateQueries({ queryKey: ['groups', groupId] })
      queryClient.invalidateQueries({ queryKey: ['groups'] })
    },
  })
}
