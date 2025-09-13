/**
 * Хуки для работы с группами
 */

import { useCreate, useReadList, useReadOne, useUpdate, useDelete } from './useCrud'
import type { VKGroup, GroupsResponse, CreateGroupRequest, UpdateGroupRequest, GroupsFilters } from '@/entities/groups'

// Хук для создания группы
export function useCreateGroup() {
  return useCreate<VKGroup, CreateGroupRequest>('/api/v1/groups', {
    successMessage: 'Группа успешно создана',
    errorMessage: 'Ошибка при создании группы',
  })
}

// Хук для получения списка групп
export function useGroups(params?: GroupsFilters) {
  return useReadList<GroupsResponse>('/api/v1/groups', params as Record<string, unknown>)
}

// Хук для получения одной группы
export function useGroup(id: number) {
  return useReadOne<VKGroup>('/api/v1/groups', id)
}

// Хук для обновления группы
export function useUpdateGroup(id: number) {
  return useUpdate<VKGroup, UpdateGroupRequest>(`/api/v1/groups/${id}`, {
    successMessage: 'Группа успешно обновлена',
    errorMessage: 'Ошибка при обновлении группы',
  })
}

// Хук для удаления группы
export function useDeleteGroup(id: number) {
  return useDelete<VKGroup>(`/api/v1/groups/${id}`, {
    successMessage: 'Группа успешно удалена',
    errorMessage: 'Ошибка при удалении группы',
  })
}