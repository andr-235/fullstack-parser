import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { groupsApi } from '@/services/api'

export const useGroupsStore = defineStore('groups', () => {
  // State
  const groups = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const filters = ref({
    status: 'all',
    search: '',
    sortBy: 'uploadedAt',
    sortOrder: 'desc'
  })
  const pagination = ref({
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

    // Сортировка
    filtered.sort((a, b) => {
      const aVal = a[filters.value.sortBy]
      const bVal = b[filters.value.sortBy]
      return filters.value.sortOrder === 'asc' ? aVal - bVal : bVal - aVal
    })

    return filtered
  })

  // Actions
  const uploadGroups = async (file, encoding) => {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('encoding', encoding)
      
      const response = await groupsApi.uploadGroups(formData, encoding)
      currentTask.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchGroups = async (params = {}) => {
    loading.value = true
    try {
      const response = await groupsApi.getGroups({
        ...pagination.value,
        ...filters.value,
        ...params
      })
      groups.value = response.data.groups
      pagination.value.total = response.data.total
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const pollTaskStatus = async (taskId) => {
    try {
      const response = await groupsApi.getTaskStatus(taskId)
      
      // Сохраняем данные из response.data.data, а не response.data
      currentTask.value = response.data.data
      
      if (response.data.data.status === 'completed') {
        await fetchGroups()
      }
      
      return response.data.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const deleteGroup = async (groupId) => {
    try {
      await groupsApi.deleteGroup(groupId)
      groups.value = groups.value.filter(g => g.id !== groupId)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const deleteGroups = async (groupIds) => {
    try {
      await groupsApi.deleteGroups(groupIds)
      groups.value = groups.value.filter(g => !groupIds.includes(g.id))
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.page = 1
    fetchGroups()
  }

  const clearError = () => {
    error.value = null
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
    
    // Actions
    uploadGroups,
    fetchGroups,
    pollTaskStatus,
    deleteGroup,
    deleteGroups,
    updateFilters,
    clearError
  }
})
