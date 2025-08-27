// Groups hooks types
import type {
  VKGroupResponse,
  VKGroupCreate,
  VKGroupUpdate,
  PaginationParams,
} from '@/shared/types'
import type { GroupsFilters, SortConfig } from './groups.types'

// Типы для параметров хуков
export interface UseGroupsParams extends PaginationParams {
  active_only?: boolean
}

export interface UseInfiniteGroupsParams extends GroupsFilters {
  pageSize?: number
}

export interface UseGroupParams {
  groupId: number
  enabled?: boolean
}

export interface UseGroupStatsParams {
  groupId: number
  enabled?: boolean
}

// Типы для мутаций
export interface CreateGroupParams extends VKGroupCreate {}

export interface UpdateGroupParams {
  groupId: number
  data: VKGroupUpdate
}

export interface DeleteGroupParams {
  groupId: number
}

export interface RefreshGroupParams {
  groupId: number
}

// Типы для возвращаемых значений хуков
export interface GroupsQueryResult {
  data: VKGroupResponse[] | undefined
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

export interface InfiniteGroupsQueryResult {
  data: VKGroupResponse[] | undefined
  isLoading: boolean
  error: Error | null
  hasNextPage: boolean
  isFetchingNextPage: boolean
  fetchNextPage: () => void
  refetch: () => void
}

export interface GroupQueryResult {
  data: VKGroupResponse | undefined
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

export interface GroupStatsQueryResult {
  data: any | undefined
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

// Типы для мутаций
export interface GroupMutationResult {
  mutate: (params: any) => void
  mutateAsync: (params: any) => Promise<any>
  isLoading: boolean
  isError: boolean
  error: Error | null
  isSuccess: boolean
  data: any
  reset: () => void
}

// Типы для оптимизации кэша
export interface GroupsCacheConfig {
  staleTime: number
  gcTime: number
  refetchOnWindowFocus: boolean
  refetchOnReconnect: boolean
}

// Типы для обработки ошибок
export interface GroupsErrorHandler {
  onError: (error: Error) => void
  onSuccess: (data: any) => void
  onSettled: (data: any, error: Error | null) => void
}
