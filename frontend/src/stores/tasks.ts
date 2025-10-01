import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tasksApi, getTaskStatus } from '@/services/api'
import type { Task, VkCollectTaskData } from '@/types/api'
import { useAdaptivePolling, type UseAdaptivePollingReturn } from '@/composables/useAdaptivePolling'

interface TaskProgress {
  posts: number
  comments: number
}

interface TasksFilters {
  status: string
}

export const useTasksStore = defineStore('tasks', () => {
  // State
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const currentTaskId = ref<string | number | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string[]>([])
  const progress = ref<TaskProgress>({ posts: 0, comments: 0 })

  // Адаптивный polling
  const activePolling = ref<UseAdaptivePollingReturn | null>(null)
  const pollingTaskId = ref<string | null>(null)

  // Filters
  const filters = ref<TasksFilters>({
    status: ''
  })

  // Pagination
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  })

  // Computed
  const isTaskRunning = computed(() => {
    return currentTask.value?.status === 'processing'
  })

  const isPollingActive = computed(() => {
    return activePolling.value?.isPolling || false
  })

  const pollingStatus = computed(() => {
    if (!activePolling.value) return null
    return {
      isPolling: activePolling.value.isPolling,
      currentInterval: activePolling.value.currentInterval,
      retryCount: activePolling.value.retryCount,
      lastError: activePolling.value.lastError || null,
      currentStatus: activePolling.value.currentStatus || null
    }
  })

  const isEmpty = computed(() => {
    return !loading.value && tasks.value.length === 0
  })

  const hasError = computed(() => {
    return error.value.length > 0
  })

  const errorMessage = computed(() => {
    return error.value.join('; ')
  })

  // Actions
  const createVkCollectTask = async (data: VkCollectTaskData) => {
    loading.value = true
    try {
      const response = await tasksApi.createVkCollectTask(data)
      currentTaskId.value = response.data.data.taskId
      await fetchTasks()
      return response.data.data
    } catch (err: any) {
      error.value.push(err.response?.data?.error || err.response?.data?.message || 'Ошибка создания задачи')
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchTasks = async (params = {}) => {
    loading.value = true
    try {
      const response = await tasksApi.getTasks({
        page: pagination.value.page,
        limit: pagination.value.limit,
        status: filters.value.status || undefined,
        ...params
      })
      // Backend возвращает: { success: true, data: [...tasks], pagination: {...} }
      tasks.value = response.data.data || []
      pagination.value.total = response.data.pagination?.total || 0
      pagination.value.totalPages = response.data.pagination?.totalPages || 0
    } catch (err: any) {
      error.value.push(err.response?.data?.error || err.response?.data?.message || 'Ошибка загрузки задач')
    } finally {
      loading.value = false
    }
  }

  /**
   * Запуск адаптивного polling для отслеживания статуса задачи
   * @param taskId ID задачи для отслеживания
   * @param taskType Тип задачи (vk-collect, export, general)
   */
  const startAdaptivePolling = async (taskId: string | number, taskType: string = 'vk-collect') => {
    // Останавливаем предыдущий polling если активен
    stopPolling()

    const taskIdStr = String(taskId)
    pollingTaskId.value = taskIdStr

    console.log(`Запуск адаптивного polling для задачи ${taskIdStr} (тип: ${taskType})`)

    // Создаем новый экземпляр адаптивного polling
    activePolling.value = useAdaptivePolling(taskIdStr, taskType)

    // Запускаем polling с функцией обновления статуса
    await activePolling.value?.startPolling(async () => {
      try {
        const response = await getTaskStatus(taskId)
        const status = response.data.data || response.data

        // Обновляем прогресс задачи
        if (status.progress && typeof status.progress === 'object') {
          progress.value = {
            posts: (status.progress as any).posts || (status.progress as any).processed || 0,
            comments: (status.progress as any).comments || 0
          }
        }

        // Обновляем ошибки
        if (status.errors && Array.isArray(status.errors)) {
          error.value = status.errors
        }

        // Если задача завершена, обновляем список задач
        if (['completed', 'failed'].includes(status.status)) {
          console.log(`Задача ${taskIdStr} завершена со статусом: ${status.status}`)
          await fetchTasks()
        }

        return {
          status: status.status || 'pending',
          progress: status.progress,
          errors: status.errors,
          data: status
        }
      } catch (err: any) {
        const errorMsg = err.response?.data?.error || err.response?.data?.message || 'Ошибка получения статуса'
        console.error(`Ошибка polling для задачи ${taskIdStr}:`, errorMsg)

        // Добавляем ошибку в общий список, но не останавливаем polling
        // (это будет обработано адаптивным polling'ом)
        if (!error.value.includes(errorMsg)) {
          error.value.push(errorMsg)
        }

        throw err
      }
    })
  }

  /**
   * Остановка активного polling
   */
  const stopPolling = () => {
    if (activePolling.value) {
      console.log(`Остановка polling для задачи ${pollingTaskId.value}`)
      activePolling.value.stopPolling()
      activePolling.value = null
      pollingTaskId.value = null
    }
  }

  /**
   * Сброс состояния polling (для перезапуска)
   */
  const resetPolling = () => {
    if (activePolling.value) {
      activePolling.value.resetPolling()
    }
  }

  /**
   * Обратная совместимость со старым API
   * @deprecated Используйте startAdaptivePolling
   */
  const startPolling = (taskId: string | number) => {
    console.warn('startPolling deprecated, используйте startAdaptivePolling')
    return startAdaptivePolling(taskId, 'vk-collect')
  }

  const getTaskById = async (taskId: string | number) => {
    try {
      const response = await tasksApi.getTaskDetails(taskId)
      currentTask.value = response.data.data || response.data
      return response.data.data || response.data
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || err.response?.data?.message || 'Ошибка загрузки задачи'
      console.error('Task fetch error:', errorMsg)
      throw err
    }
  }

  const clearErrors = () => {
    error.value = []
  }

  const createCommentsTask = async (data: VkCollectTaskData) => {
    try {
      const response = await tasksApi.createVkCollectTask(data)
      return response.data.data
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || err.response?.data?.message || 'Ошибка создания задачи'
      console.error('Task creation error:', errorMsg)
      throw err
    }
  }

  const changePage = (page: number) => {
    pagination.value.page = page
    fetchTasks()
  }

  const setStatusFilter = (status: string) => {
    filters.value.status = status
    pagination.value.page = 1
    fetchTasks()
  }

  return {
    // State
    tasks,
    currentTask,
    currentTaskId,
    loading,
    error,
    progress,
    pagination,
    filters,

    // Polling state
    pollingTaskId,
    isPollingActive,
    pollingStatus,

    // Computed
    isTaskRunning,
    isEmpty,
    hasError,
    errorMessage,

    // Actions
    createVkCollectTask,
    fetchTasks,
    getTaskById,
    clearErrors,
    createCommentsTask,
    changePage,
    setStatusFilter,

    // Polling methods
    startAdaptivePolling,
    startPolling, // deprecated, для обратной совместимости
    stopPolling,
    resetPolling
  }
})