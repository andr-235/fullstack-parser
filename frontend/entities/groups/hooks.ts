import { useState, useEffect } from 'react'
import { apiClient } from '@/shared/lib'
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

export const useGroups = (filters?: GroupsFilters) => {
  const [groups, setGroups] = useState<VKGroup[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchGroups = async () => {
    setLoading(true)
    setError(null)
    try {
      const response: GroupsResponse = await apiClient.getGroups(filters)
      setGroups(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch groups')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGroups()
  }, [
    filters?.is_active,
    filters?.active_only,
    filters?.search,
    filters?.has_monitoring,
    filters?.min_members,
    filters?.max_members,
    filters?.page,
    filters?.size,
  ])

  const createGroup = async (groupData: CreateGroupRequest): Promise<VKGroup> => {
    try {
      const newGroup: VKGroup = await apiClient.createGroup(groupData)
      setGroups(prev => [newGroup, ...prev])
      return newGroup
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create group')
    }
  }

  const updateGroup = async (id: number, updates: UpdateGroupRequest): Promise<VKGroup> => {
    try {
      const updatedGroup: VKGroup = await apiClient.updateGroup(id, updates)
      setGroups(prev => prev.map(group => (group.id === id ? updatedGroup : group)))
      return updatedGroup
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update group')
    }
  }

  const deleteGroup = async (id: number): Promise<void> => {
    try {
      await apiClient.deleteGroup(id)
      setGroups(prev => prev.filter(group => group.id !== id))
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to delete group')
    }
  }

  const toggleGroupStatus = async (id: number, isActive: boolean): Promise<VKGroup> => {
    return updateGroup(id, { is_active: isActive })
  }

  return {
    groups,
    loading,
    error,
    createGroup,
    updateGroup,
    deleteGroup,
    toggleGroupStatus,
    refetch: fetchGroups,
  }
}

export const useGroup = (id: number) => {
  const [group, setGroup] = useState<VKGroup | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchGroup = async () => {
    if (!id) return

    setLoading(true)
    setError(null)
    try {
      const data: VKGroup = await apiClient.getGroup(id)
      setGroup(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch group')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGroup()
  }, [id])

  return {
    group,
    loading,
    error,
    refetch: fetchGroup,
  }
}

export const useGroupStats = (id: number) => {
  const [stats, setStats] = useState<GroupStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    if (!id) return

    setLoading(true)
    setError(null)
    try {
      const data: GroupStats = await apiClient.getGroupStats(id)
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch group stats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [id])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
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

      const result: UploadGroupsResponse = await apiClient.uploadGroups(formData)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload groups')
      throw err
    } finally {
      setUploading(false)
    }
  }

  const getUploadProgress = async (uploadId: string): Promise<UploadProgress> => {
    try {
      // TODO: Implement upload progress tracking
      // const progress: UploadProgress = await apiClient.getGroupsUploadProgress(uploadId)
      const progress: UploadProgress = {
        loaded: 1,
        total: 1,
        percentage: 100,
        status: 'completed',
        progress: 100,
        current_group: 'Upload completed',
        total_groups: 0,
        processed_groups: 0,
        created: 0,
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
  const [stats, setStats] = useState<GroupsStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = async () => {
    setLoading(true)
    setError(null)
    try {
      const data: GroupsStats = await apiClient.getGroupsOverviewStats()
      setStats(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch groups stats')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStats()
  }, [])

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  }
}

export const useGroupBulkOperations = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const activateGroups = async (actionData: GroupBulkAction): Promise<GroupBulkResponse> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.bulkActivateGroups(actionData)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to activate groups'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const deactivateGroups = async (actionData: GroupBulkAction): Promise<GroupBulkResponse> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.bulkDeactivateGroups(actionData)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to deactivate groups'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return {
    activateGroups,
    deactivateGroups,
    loading,
    error,
  }
}

export const useGroupActions = (id: number) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const activateGroup = async (): Promise<VKGroup> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.activateGroup(id)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to activate group'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const deactivateGroup = async (): Promise<VKGroup> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.deactivateGroup(id)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to deactivate group'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getGroupByVkId = async (vkId: number): Promise<VKGroup> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.getGroupByVkId(vkId)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch group by VK ID'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const getGroupByScreenName = async (screenName: string): Promise<VKGroup> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.getGroupByScreenName(screenName)
      return result
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to fetch group by screen name'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const searchGroups = async (q: string, filters?: GroupsFilters): Promise<GroupsResponse> => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.searchGroups(q, filters)
      return result
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to search groups'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return {
    activateGroup,
    deactivateGroup,
    getGroupByVkId,
    getGroupByScreenName,
    searchGroups,
    loading,
    error,
  }
}
