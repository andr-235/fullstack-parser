import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

import { httpClient } from '@/shared/lib'

import {
  VKGroup,
  GroupsResponse,
  CreateGroupRequest,
  UpdateGroupRequest,
  GroupsFilters,
  GroupStats,
  GroupsStats,
  GroupBulkAction,
  GroupBulkResponse,
  UploadGroupsResponse,
  UploadProgress,
} from './types'

// Query Keys для React Query
export const groupsKeys = {
  all: ['groups'] as const,
  lists: () => [...groupsKeys.all, 'list'] as const,
  list: (filters?: GroupsFilters) => [...groupsKeys.lists(), filters] as const,
  details: () => [...groupsKeys.all, 'detail'] as const,
  detail: (id: number) => [...groupsKeys.details(), id] as const,
  stats: () => [...groupsKeys.all, 'stats'] as const,
  overviewStats: () => [...groupsKeys.stats(), 'overview'] as const,
}

export const useGroups = (filters?: GroupsFilters, autoFetch: boolean = true) => {
  const queryClient = useQueryClient()

  // React Query для получения списка групп
  const {
    data: groupsResponse,
    isLoading: loading,
    error,
    refetch,
  } = useQuery({
    queryKey: groupsKeys.list(filters),
    queryFn: async (): Promise<GroupsResponse> => {
      return httpClient.get('/api/groups', { params: filters })
    },
    enabled: autoFetch,
    staleTime: 5 * 60 * 1000, // 5 минут
    gcTime: 10 * 60 * 1000, // 10 минут
    retry: 3,
    retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
  })

  // Мутация для создания группы
  const createGroupMutation = useMutation({
    mutationFn: async (groupData: CreateGroupRequest): Promise<VKGroup> => {
      return httpClient.post('/api/groups', groupData)
    },
    onSuccess: () => {
      // Инвалидируем список групп после создания
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
    },
  })

  // Мутация для обновления группы
  const updateGroupMutation = useMutation({
    mutationFn: async ({
      id,
      updates,
    }: {
      id: number
      updates: UpdateGroupRequest
    }): Promise<VKGroup> => {
      return httpClient.put(`/api/groups/${id}`, updates)
    },
    onSuccess: (data: VKGroup) => {
      // Инвалидируем список групп и детали группы
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
      queryClient.invalidateQueries({ queryKey: groupsKeys.detail(data.id) })
    },
  })

  // Мутация для удаления группы
  const deleteGroupMutation = useMutation({
    mutationFn: async (id: number): Promise<void> => {
      return httpClient.delete(`/api/groups/${id}`)
    },
    onSuccess: () => {
      // Инвалидируем список групп
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
    },
  })

  // Мутация для переключения статуса группы
  const toggleGroupStatusMutation = useMutation({
    mutationFn: async ({ id, isActive }: { id: number; isActive: boolean }): Promise<VKGroup> => {
      return httpClient.put(`/api/groups/${id}`, { is_active: isActive })
    },
    onSuccess: (data: VKGroup) => {
      // Инвалидируем список групп и детали группы
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
      queryClient.invalidateQueries({ queryKey: groupsKeys.detail(data.id) })
    },
  })

  // Обертки для совместимости с существующим API
  const createGroup = async (groupData: CreateGroupRequest): Promise<VKGroup> => {
    return createGroupMutation.mutateAsync(groupData)
  }

  const updateGroup = async (id: number, updates: UpdateGroupRequest): Promise<VKGroup> => {
    return updateGroupMutation.mutateAsync({ id, updates })
  }

  const deleteGroup = async (id: number): Promise<void> => {
    return deleteGroupMutation.mutateAsync(id)
  }

  const toggleGroupStatus = async (id: number, isActive: boolean): Promise<VKGroup> => {
    return toggleGroupStatusMutation.mutateAsync({ id, isActive })
  }

  return {
    groups: groupsResponse?.items || [],
    loading,
    error: error?.message || null,
    pagination: {
      total: groupsResponse?.total || 0,
      page: groupsResponse?.page || 1,
      size: groupsResponse?.size || 20,
      pages: groupsResponse?.pages || 0,
    },
    createGroup,
    updateGroup,
    deleteGroup,
    toggleGroupStatus,
    refetch,
  }
}

export const useGroup = (id: number) => {
  const {
    data: group,
    isLoading: loading,
    error,
    refetch,
  } = useQuery({
    queryKey: groupsKeys.detail(id),
    queryFn: async (): Promise<VKGroup> => {
      return httpClient.get(`/api/groups/${id}`)
    },
    enabled: !!id,
    staleTime: 10 * 60 * 1000, // 10 минут
    gcTime: 30 * 60 * 1000, // 30 минут
    retry: 3,
  })

  return {
    group: group || null,
    loading,
    error: error?.message || null,
    refetch,
  }
}

export const useGroupStats = (id: number) => {
  const {
    data: stats,
    isLoading: loading,
    error,
    refetch,
  } = useQuery({
    queryKey: [...groupsKeys.stats(), id],
    queryFn: async (): Promise<GroupStats> => {
      return httpClient.get(`/api/groups/${id}/stats`)
    },
    enabled: !!id,
    staleTime: 2 * 60 * 1000, // 2 минуты
    gcTime: 5 * 60 * 1000, // 5 минут
    retry: 3,
  })

  return {
    stats: stats || null,
    loading,
    error: error?.message || null,
    refetch,
  }
}

export const useUploadGroups = () => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const uploadGroups = async (
    file: File,
    isActive: boolean = true,
    maxPostsToCheck: number = 100
  ): Promise<UploadGroupsResponse> => {
    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_active', isActive.toString())
      formData.append('max_posts_to_check', maxPostsToCheck.toString())

      const result: UploadGroupsResponse = await httpClient.post('/api/groups/upload', formData)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload groups')
      throw err
    } finally {
      setUploading(false)
    }
  }

  const getUploadProgress = async (_uploadId: string): Promise<UploadProgress> => {
    try {
      // TODO: Implement upload progress tracking
      // const progress: UploadProgress = await httpClient.getGroupsUploadProgress(uploadId)
      const progress: UploadProgress = {
        loaded: 1,
        total: 1,
        percentage: 100,
        status: 'completed',
        progress: 100,
        current_group: 'Upload completed',
        total_groups: 0,
        processed_groups: 0,
        processed: 0,
        created: 0,
        updated: 0,
        skipped: 0,
        errors: [],
      }
      setUploadProgress(progress)
      return progress
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to get upload progress')
    }
  }

  return {
    uploadGroups,
    getUploadProgress,
    uploadProgress,
    uploading,
    error,
  }
}

export const useGroupsStats = () => {
  const {
    data: stats,
    isLoading: loading,
    error,
    refetch,
  } = useQuery({
    queryKey: groupsKeys.overviewStats(),
    queryFn: async (): Promise<GroupsStats> => {
      return httpClient.get('/api/groups/overview-stats')
    },
    staleTime: 2 * 60 * 1000, // 2 минуты
    gcTime: 5 * 60 * 1000, // 5 минут
    retry: 3,
  })

  return {
    stats: stats || null,
    loading,
    error: error?.message || null,
    refetch,
  }
}

export const useGroupBulkOperations = () => {
  const queryClient = useQueryClient()

  const activateGroupsMutation = useMutation({
    mutationFn: async (actionData: GroupBulkAction): Promise<GroupBulkResponse> => {
      return httpClient.post('/api/groups/bulk-activate', actionData)
    },
    onSuccess: () => {
      // Инвалидируем список групп после массовой активации
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
    },
  })

  const deactivateGroupsMutation = useMutation({
    mutationFn: async (actionData: GroupBulkAction): Promise<GroupBulkResponse> => {
      return httpClient.post('/api/groups/bulk-deactivate', actionData)
    },
    onSuccess: () => {
      // Инвалидируем список групп после массовой деактивации
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
    },
  })

  const activateGroups = async (actionData: GroupBulkAction): Promise<GroupBulkResponse> => {
    return activateGroupsMutation.mutateAsync(actionData)
  }

  const deactivateGroups = async (actionData: GroupBulkAction): Promise<GroupBulkResponse> => {
    return deactivateGroupsMutation.mutateAsync(actionData)
  }

  return {
    activateGroups,
    deactivateGroups,
    loading: activateGroupsMutation.isPending || deactivateGroupsMutation.isPending,
    error: activateGroupsMutation.error?.message || deactivateGroupsMutation.error?.message || null,
  }
}

export const useGroupActions = (id: number) => {
  const queryClient = useQueryClient()

  const activateGroupMutation = useMutation({
    mutationFn: async (): Promise<VKGroup> => {
      return httpClient.put(`/api/groups/${id}/activate`)
    },
    onSuccess: (data: VKGroup) => {
      // Инвалидируем список групп и детали группы
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
      queryClient.invalidateQueries({ queryKey: groupsKeys.detail(data.id) })
    },
  })

  const deactivateGroupMutation = useMutation({
    mutationFn: async (): Promise<VKGroup> => {
      return httpClient.put(`/api/groups/${id}/deactivate`)
    },
    onSuccess: (data: VKGroup) => {
      // Инвалидируем список групп и детали группы
      queryClient.invalidateQueries({ queryKey: groupsKeys.lists() })
      queryClient.invalidateQueries({ queryKey: groupsKeys.detail(data.id) })
    },
  })

  const getGroupByVkIdMutation = useMutation({
    mutationFn: async (vkId: number): Promise<VKGroup> => {
      return httpClient.get(`/api/groups/vk/${vkId}`)
    },
  })

  const getGroupByScreenNameMutation = useMutation({
    mutationFn: async (screenName: string): Promise<VKGroup> => {
      return httpClient.get(`/api/groups/screen/${screenName}`)
    },
  })

  const searchGroupsMutation = useMutation({
    mutationFn: async ({
      q,
      filters,
    }: {
      q: string
      filters?: GroupsFilters
    }): Promise<GroupsResponse> => {
      return httpClient.get('/api/groups/search', { params: { q, ...filters } })
    },
  })

  const activateGroup = async (): Promise<VKGroup> => {
    return activateGroupMutation.mutateAsync()
  }

  const deactivateGroup = async (): Promise<VKGroup> => {
    return deactivateGroupMutation.mutateAsync()
  }

  const getGroupByVkId = async (vkId: number): Promise<VKGroup> => {
    return getGroupByVkIdMutation.mutateAsync(vkId)
  }

  const getGroupByScreenName = async (screenName: string): Promise<VKGroup> => {
    return getGroupByScreenNameMutation.mutateAsync(screenName)
  }

  const searchGroups = async (q: string, filters?: GroupsFilters): Promise<GroupsResponse> => {
    return searchGroupsMutation.mutateAsync({ q, filters: filters || {} })
  }

  const isLoading =
    activateGroupMutation.isPending ||
    deactivateGroupMutation.isPending ||
    getGroupByVkIdMutation.isPending ||
    getGroupByScreenNameMutation.isPending ||
    searchGroupsMutation.isPending

  const error =
    activateGroupMutation.error?.message ||
    deactivateGroupMutation.error?.message ||
    getGroupByVkIdMutation.error?.message ||
    getGroupByScreenNameMutation.error?.message ||
    searchGroupsMutation.error?.message ||
    null

  return {
    activateGroup,
    deactivateGroup,
    getGroupByVkId,
    getGroupByScreenName,
    searchGroups,
    loading: isLoading,
    error,
  }
}
