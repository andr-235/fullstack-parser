import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTasksStore } from '@/stores/tasks'

// Мокаем API
vi.mock('@/services/api', () => ({
  tasksApi: {
    getTasks: vi.fn(),
    createVkCollectTask: vi.fn(),
    getTaskDetails: vi.fn()
  },
  postCreateTask: vi.fn(),
  postStartCollect: vi.fn(),
  getTaskStatus: vi.fn()
}))

describe('Tasks Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const store = useTasksStore()

      // Single task state
      expect(store.taskId).toBe(null)
      expect(store.status).toBe('')
      expect(store.progress).toEqual({ posts: 0, comments: 0 })
      expect(store.errors).toEqual([])

      // Tasks list state
      expect(store.tasks).toEqual([])
      expect(store.loading).toBe(false)
      expect(store.error).toBe(null)
      expect(store.pagination).toEqual({
        page: 1,
        limit: 20,
        total: 0,
        totalPages: 0
      })
      expect(store.filters).toEqual({
        status: ''
      })
    })
  })

  describe('Tasks List Actions', () => {
    it('should fetch tasks successfully', async () => {
      const store = useTasksStore()
      const mockTasks = [
        { id: 1, type: 'comments', status: 'pending' },
        { id: 2, type: 'vk_collect', status: 'completed' }
      ]

      const mockResponse = {
        data: {
          tasks: mockTasks,
          total: 2,
          totalPages: 1
        }
      }

      // Мокаем API
      const { tasksApi } = await import('@/services/api')
      tasksApi.getTasks.mockResolvedValueOnce(mockResponse)

      await store.fetchTasks()

      expect(store.loading).toBe(false)
      expect(store.tasks).toEqual(mockTasks)
      expect(store.pagination.total).toBe(2)
      expect(store.pagination.totalPages).toBe(1)
      expect(store.error).toBe(null)
    })

    it('should handle fetch tasks error', async () => {
      const store = useTasksStore()
      const errorMessage = 'Failed to fetch tasks'

      const { tasksApi } = await import('@/services/api')
      tasksApi.getTasks.mockRejectedValueOnce({
        response: { data: { message: errorMessage } }
      })

      await store.fetchTasks()

      expect(store.loading).toBe(false)
      expect(store.tasks).toEqual([])
      expect(store.error).toBe(errorMessage)
    })

    it('should set loading state during fetch', async () => {
      const store = useTasksStore()

      const { tasksApi } = await import('@/services/api')
      // Создаем промис, который не резолвится сразу
      let resolvePromise
      const pendingPromise = new Promise(resolve => {
        resolvePromise = resolve
      })
      tasksApi.getTasks.mockReturnValueOnce(pendingPromise)

      // Запускаем fetch
      const fetchPromise = store.fetchTasks()

      // Проверяем, что loading = true
      expect(store.loading).toBe(true)

      // Резолвим промис
      resolvePromise({ data: { tasks: [], total: 0, totalPages: 0 } })
      await fetchPromise

      // Проверяем, что loading = false
      expect(store.loading).toBe(false)
    })
  })

  describe('VK Collect Task Creation', () => {
    it('should create VK collect task successfully', async () => {
      const store = useTasksStore()
      const taskData = {
        groups: [12345, 67890],
        token: 'test-token'
      }
      const mockResponse = {
        data: { taskId: 'task-123' }
      }

      const { tasksApi } = await import('@/services/api')
      tasksApi.createVkCollectTask.mockResolvedValueOnce(mockResponse)
      tasksApi.getTasks.mockResolvedValueOnce({ data: { tasks: [], total: 0, totalPages: 0 } })

      const result = await store.createVkCollectTask(taskData)

      expect(tasksApi.createVkCollectTask).toHaveBeenCalledWith(taskData)
      expect(tasksApi.getTasks).toHaveBeenCalled() // Должен обновить список задач
      expect(result).toEqual(mockResponse.data)
      expect(store.error).toBe(null)
    })

    it('should handle VK collect task creation error', async () => {
      const store = useTasksStore()
      const taskData = { groups: [12345], token: 'test-token' }
      const errorMessage = 'Invalid token'

      const { tasksApi } = await import('@/services/api')
      tasksApi.createVkCollectTask.mockRejectedValueOnce({
        response: { data: { message: errorMessage } }
      })

      await expect(store.createVkCollectTask(taskData)).rejects.toThrow(errorMessage)
      expect(store.error).toBe(errorMessage)
    })
  })

  describe('Pagination', () => {
    it('should set page correctly', () => {
      const store = useTasksStore()

      store.setPage(2)

      expect(store.pagination.page).toBe(2)
    })

    it('should set status filter and reset page', () => {
      const store = useTasksStore()
      store.pagination.page = 3

      store.setStatusFilter('completed')

      expect(store.filters.status).toBe('completed')
      expect(store.pagination.page).toBe(1) // Должна сброситься на первую страницу
    })

    it('should clear status filter', () => {
      const store = useTasksStore()
      store.filters.status = 'completed'

      store.setStatusFilter('')

      expect(store.filters.status).toBe('')
    })
  })

  describe('Computed Properties', () => {
    it('should calculate hasNextPage correctly', () => {
      const store = useTasksStore()

      // Нет следующей страницы
      store.pagination.page = 1
      store.pagination.totalPages = 1
      expect(store.hasNextPage).toBe(false)

      // Есть следующая страница
      store.pagination.page = 1
      store.pagination.totalPages = 2
      expect(store.hasNextPage).toBe(true)

      // Последняя страница
      store.pagination.page = 2
      store.pagination.totalPages = 2
      expect(store.hasNextPage).toBe(false)
    })

    it('should calculate hasPrevPage correctly', () => {
      const store = useTasksStore()

      // Первая страница
      store.pagination.page = 1
      expect(store.hasPrevPage).toBe(false)

      // Не первая страница
      store.pagination.page = 2
      expect(store.hasPrevPage).toBe(true)
    })

    it('should calculate isEmpty correctly', () => {
      const store = useTasksStore()

      // Загрузка
      store.loading = true
      store.tasks = []
      expect(store.isEmpty).toBe(false)

      // Пустой список после загрузки
      store.loading = false
      store.tasks = []
      expect(store.isEmpty).toBe(true)

      // Непустой список
      store.loading = false
      store.tasks = [{ id: 1 }]
      expect(store.isEmpty).toBe(false)
    })
  })

  describe('Single Task Management', () => {
    it('should create task and set initial state', async () => {
      const store = useTasksStore()
      const taskData = {
        ownerId: -123,
        postId: 456,
        token: 'test-token'
      }
      const mockResponse = {
        data: { taskId: 'task-123' }
      }

      const { postCreateTask } = await import('@/services/api')
      postCreateTask.mockResolvedValueOnce(mockResponse)

      await store.createTask(taskData)

      expect(store.taskId).toBe('task-123')
      expect(store.status).toBe('created')
      expect(store.errors).toEqual([])
    })

    it('should handle create task error', async () => {
      const store = useTasksStore()
      const taskData = { ownerId: -123, postId: 456, token: 'test-token' }
      const errorMessage = 'Invalid data'

      const { postCreateTask } = await import('@/services/api')
      postCreateTask.mockRejectedValueOnce(new Error(errorMessage))

      await expect(store.createTask(taskData)).rejects.toThrow(errorMessage)
      expect(store.errors).toContain(errorMessage)
    })

    it('should start collect and begin polling', async () => {
      const store = useTasksStore()
      store.taskId = 'task-123'

      const { postStartCollect } = await import('@/services/api')
      postStartCollect.mockResolvedValueOnce({})

      await store.startCollect()

      expect(store.status).toBe('pending')
      expect(postStartCollect).toHaveBeenCalledWith('task-123')
    })

    it('should not start collect without taskId', async () => {
      const store = useTasksStore()
      store.taskId = null

      await expect(store.startCollect()).rejects.toThrow('Task ID не установлен')
    })
  })

  describe('Polling', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should stop polling when task is completed', async () => {
      const store = useTasksStore()
      store.taskId = 'task-123'

      const { getTaskStatus } = await import('@/services/api')
      getTaskStatus.mockResolvedValue({
        data: {
          status: 'completed',
          progress: { posts: 10, comments: 100 },
          errors: []
        }
      })

      store.pollStatus()

      // Продвигаем таймер на 5 секунд
      vi.advanceTimersByTime(5000)
      await vi.runAllTimersAsync()

      expect(store.status).toBe('completed')
      expect(store.progress).toEqual({ posts: 10, comments: 100 })

      // Продвигаем таймер еще на 5 секунд - polling должен остановиться
      getTaskStatus.mockClear()
      vi.advanceTimersByTime(5000)

      expect(getTaskStatus).not.toHaveBeenCalled()
    })

    it('should continue polling for processing status', async () => {
      const store = useTasksStore()
      store.taskId = 'task-123'

      const { getTaskStatus } = await import('@/services/api')
      getTaskStatus.mockResolvedValue({
        data: {
          status: 'processing',
          progress: { posts: 5, comments: 50 },
          errors: []
        }
      })

      store.pollStatus()

      // Первый вызов
      vi.advanceTimersByTime(5000)
      await vi.runAllTimersAsync()

      expect(store.status).toBe('processing')

      // Второй вызов
      vi.advanceTimersByTime(5000)
      await vi.runAllTimersAsync()

      expect(getTaskStatus).toHaveBeenCalledTimes(2)
    })

    it('should stop polling manually', () => {
      const store = useTasksStore()
      store.taskId = 'task-123'

      store.pollStatus()
      store.stopPolling()

      const { getTaskStatus } = import('@/services/api')
      vi.advanceTimersByTime(5000)

      // Polling не должен выполняться после остановки
      expect(getTaskStatus).not.toHaveBeenCalled()
    })
  })
})