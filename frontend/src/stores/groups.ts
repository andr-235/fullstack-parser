import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { groupsApi } from '@/services/api'
import type { Group, GroupUploadResponse, TaskStatus } from '@/types/api'

interface GroupsFilters {
  status: string
  search: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
}

interface GroupsPagination {
  page: number
  limit: number
  total: number
}

export const useGroupsStore = defineStore('groups', () => {
  // State
  const groups = ref<Group[]>([])
  const currentTask = ref<GroupUploadResponse | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const filters = ref<GroupsFilters>({
    status: 'all',
    search: '',
    sortBy: 'uploaded_at',
    sortOrder: 'desc'
  })
  const pagination = ref<GroupsPagination>({
    page: 1,
    limit: 20,
    total: 0
  })

  // Getters
  const filteredGroups = computed(() => {
    let filtered = groups.value

    // Фильтр по статусу
    if (filters.value.status !== 'all') {
      filtered = filtered.filter(group => group.status === filters.value.status)
    }

    // Поиск
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(group =>
        group.id.toString().includes(search) ||
        (group.name && group.name.toLowerCase().includes(search))
      )
    }

    return filtered
  })

  const isEmpty = computed(() => groups.value.length === 0)

  // Actions
  const uploadGroups = async (file: File, encoding: string = 'utf-8') => {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await groupsApi.uploadGroups(formData, encoding)
      currentTask.value = response.data.data || response.data
      return response.data.data || response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка загрузки файла'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchGroups = async () => {
    loading.value = true
    const params = {
      page: pagination.value.page,
      limit: pagination.value.limit,
      status: filters.value.status,
      search: filters.value.search,
      sortBy: filters.value.sortBy,
      sortOrder: filters.value.sortOrder as 'asc' | 'desc'
    }
    try {
      const response = await groupsApi.getGroups(params)
      console.log('Groups API response:', response.data) // Временная отладка
      groups.value = response.data.data?.groups || []
      pagination.value.total = response.data.data?.total || 0
    } catch (err: any) {
      console.error('Groups fetch error:', err) // Временная отладка
      error.value = err.response?.data?.message || 'Ошибка загрузки групп'
    } finally {
      loading.value = false
    }
  }

  const getTaskStatus = async (taskId: string | number) => {
    try {
      const response = await groupsApi.getTaskStatus(taskId)
      const status = response.data as any

      if (status.status === 'completed' && status.data) {
        await fetchGroups()
        currentTask.value = status.data
      }

      return status
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка получения статуса'
      throw err
    }
  }

  const deleteGroup = async (groupId: string | number) => {
    try {
      await groupsApi.deleteGroup(groupId)
      groups.value = groups.value.filter(group => group.id !== groupId)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка удаления группы'
      throw err
    }
  }

  const deleteGroups = async (groupIds: (string | number)[]) => {
    try {
      await groupsApi.deleteGroups(groupIds)
      groups.value = groups.value.filter(group => !groupIds.includes(group.id))
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка удаления групп'
      throw err
    }
  }

  const updateFilters = (newFilters: Partial<GroupsFilters & { page?: number, limit?: number }>) => {
    if (newFilters.page) {
      pagination.value.page = newFilters.page
    }
    if (newFilters.limit) {
      pagination.value.limit = newFilters.limit
    }

    // Обновляем фильтры, исключая page и limit
    const { page, limit, ...filterUpdates } = newFilters
    filters.value = { ...filters.value, ...filterUpdates }

    if (!newFilters.page) {
      pagination.value.page = 1
    }
  }

  const getAllGroups = async () => {
    try {
      const response = await groupsApi.getAllGroups()
      return response.data.data?.groups || []
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Ошибка загрузки групп'
      return []
    }
  }

  return {
    // State
    groups,
    currentTask,
    loading,
    error,
    filters,
    pagination,

    // Getters
    filteredGroups,
    isEmpty,

    // Actions
    uploadGroups,
    fetchGroups,
    getTaskStatus,
    deleteGroup,
    deleteGroups,
    updateFilters,
    getAllGroups
  }
})