/**
 * API для работы с группами
 */

import { httpClient } from '@/shared/lib/http-client'
import { getRoutePath, GROUPS_ROUTES } from '@/shared/config/routes'
import type {
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
} from '@/entities/groups'

export const groupsApi = {
  async getGroups(params?: GroupsFilters): Promise<GroupsResponse> {
    const queryParams: Record<string, any> = {}

    if (params?.active_only !== undefined) {
      queryParams.is_active = params.active_only
    } else if (params?.is_active !== undefined) {
      queryParams.is_active = params.is_active
    }

    if (params?.search) queryParams.search = params.search
    if (params?.has_monitoring !== undefined) queryParams.has_monitoring = params.has_monitoring
    if (params?.min_members !== undefined) queryParams.min_members = params.min_members
    if (params?.max_members !== undefined) queryParams.max_members = params.max_members
    if (params?.page !== undefined) queryParams.page = params.page
    if (params?.size !== undefined) queryParams.size = params.size

    return httpClient.get(getRoutePath(GROUPS_ROUTES.LIST), queryParams)
  },

  async createGroup(groupData: CreateGroupRequest): Promise<VKGroup> {
    return httpClient.post(getRoutePath(GROUPS_ROUTES.CREATE), groupData)
  },

  async updateGroup(id: number, updates: UpdateGroupRequest): Promise<VKGroup> {
    return httpClient.patch(getRoutePath(GROUPS_ROUTES.UPDATE(id)), updates)
  },

  async deleteGroup(id: number): Promise<void> {
    return httpClient.delete(getRoutePath(GROUPS_ROUTES.DELETE(id)))
  },

  async getGroup(id: number): Promise<VKGroup> {
    return httpClient.get(getRoutePath(GROUPS_ROUTES.GET(id)))
  },

  async getGroupStats(id: number): Promise<GroupStats> {
    return httpClient.get(getRoutePath(GROUPS_ROUTES.STATS(id)))
  },

  async getGroupsStats(): Promise<GroupsStats> {
    return httpClient.get(getRoutePath(GROUPS_ROUTES.GLOBAL_STATS))
  },

  async bulkAction(action: GroupBulkAction): Promise<GroupBulkResponse> {
    return httpClient.post(getRoutePath(GROUPS_ROUTES.BULK), action)
  },

  async uploadGroups(file: File): Promise<UploadGroupsResponse> {
    const formData = new FormData()
    formData.append('file', file)

    return httpClient.post(getRoutePath(GROUPS_ROUTES.UPLOAD), formData)
  },

  async getUploadProgress(taskId: string): Promise<UploadProgress> {
    return httpClient.get(getRoutePath(GROUPS_ROUTES.UPLOAD_PROGRESS(taskId)))
  },
}
