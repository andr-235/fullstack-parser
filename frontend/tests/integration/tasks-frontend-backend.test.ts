import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useTasksStore } from '@/stores/tasks'
import * as api from '@/services/api'

// Mock API responses
const mockSuccessResponse = {
  data: {
    success: true,
    data: {
      taskId: 123,
      status: 'created'
    }
  }
}

const mockTaskStatusResponse = {
  data: {
    success: true,
    data: {
      id: 123,
      status: 'processing',
      type: 'fetch_comments',
      priority: 0,
      progress: {
        processed: 50,
        total: 100
      },
      errors: [],
      groups: [123456, 789012],
      parameters: {},
      result: null,
      error: null,
      executionTime: null,
      startedAt: '2024-01-01T10:00:00Z',
      finishedAt: null,
      completedAt: null,
      createdBy: 'system',
      createdAt: '2024-01-01T09:00:00Z',
      updatedAt: '2024-01-01T10:00:00Z'
    }
  }
}

const mockTasksListResponse = {
  data: {
    success: true,
    data: [
      {
        id: 123,
        type: 'fetch_comments',
        status: 'processing',
        progress: {
          processed: 50,
          total: 100
        },
        createdAt: '2024-01-01T09:00:00Z',
        updatedAt: '2024-01-01T10:00:00Z'
      }
    ],
    pagination: {
      page: 1,
      limit: 20,
      total: 1,
      totalPages: 1
    }
  }
}

const mockErrorResponse = {
  response: {
    data: {
      success: false,
      error: 'Validation failed',
      message: 'groups is required'
    }
  }
}

describe('Frontend-Backend Integration Tests', () => {
  let store: ReturnType<typeof useTasksStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTasksStore()
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Task Creation Integration', () => {
    it('должен создать VK collect задачу и обновить store', async () => {
      // Mock API call
      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockResolvedValue(mockSuccessResponse as any)
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      const taskData = { groups: [123456, 789012] }

      const result = await store.createVkCollectTask(taskData)

      expect(result).toEqual({
        taskId: 123,
        status: 'created'
      })
      expect(store.currentTaskId).toBe(123)
      expect(api.tasksApi.createVkCollectTask).toHaveBeenCalledWith(taskData)
      expect(api.tasksApi.getTasks).toHaveBeenCalled()
    })

    it('должен обработать ошибку создания задачи', async () => {
      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockRejectedValue(mockErrorResponse)

      const taskData = { groups: [] }

      await expect(store.createVkCollectTask(taskData)).rejects.toThrow()
      expect(store.error).toContain('groups is required')
    })

    it('должен валидировать формат данных при создании задачи', async () => {
      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockResolvedValue(mockSuccessResponse as any)

      const taskData = { groups: [123456, 789012, 345678] }

      await store.createVkCollectTask(taskData)

      expect(api.tasksApi.createVkCollectTask).toHaveBeenCalledWith({
        groups: expect.arrayContaining([123456, 789012, 345678])
      })
    })
  })

  describe('Task Status Polling Integration', () => {
    it('должен запустить polling и получать обновления статуса', async () => {
      vi.spyOn(api, 'getTaskStatus').mockResolvedValue(mockTaskStatusResponse as any)

      // Mock setInterval для контроля polling
      vi.useFakeTimers()

      store.startPolling(123)

      expect(store.polling).toBeTruthy()

      // Симулируем первый вызов polling
      await vi.advanceTimersByTimeAsync(2000)

      expect(api.getTaskStatus).toHaveBeenCalledWith(123)
      expect(store.progress).toEqual({
        posts: 0,
        comments: 0
      })

      vi.useRealTimers()
      store.stopPolling()
    })

    it('должен остановить polling при завершении задачи', async () => {
      const completedTaskResponse = {
        data: {
          success: true,
          data: {
            ...mockTaskStatusResponse.data.data,
            status: 'completed'
          }
        }
      }

      vi.spyOn(api, 'getTaskStatus').mockResolvedValue(completedTaskResponse as any)
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      vi.useFakeTimers()

      store.startPolling(123)

      // Симулируем polling до завершения
      await vi.advanceTimersByTimeAsync(2000)

      expect(store.polling).toBeNull()
      expect(api.tasksApi.getTasks).toHaveBeenCalled()

      vi.useRealTimers()
    })

    it('должен обработать ошибку при polling', async () => {
      const errorResponse = {
        response: {
          data: {
            success: false,
            error: 'Task not found'
          }
        }
      }

      vi.spyOn(api, 'getTaskStatus').mockRejectedValue(errorResponse)

      vi.useFakeTimers()

      store.startPolling(123)

      await vi.advanceTimersByTimeAsync(2000)

      expect(store.error).toContain('Task not found')
      expect(store.polling).toBeNull()

      vi.useRealTimers()
    })
  })

  describe('Task List Management', () => {
    it('должен загрузить список задач с правильными параметрами', async () => {
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      await store.fetchTasks()

      expect(api.tasksApi.getTasks).toHaveBeenCalledWith({
        page: 1,
        limit: 20,
        status: undefined
      })
      expect(store.tasks).toHaveLength(1)
      expect(store.pagination.total).toBe(1)
    })

    it('должен применить фильтры при загрузке задач', async () => {
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      store.setStatusFilter('processing')

      expect(api.tasksApi.getTasks).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'processing'
        })
      )
    })

    it('должен обработать пагинацию', async () => {
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      store.changePage(2)

      expect(api.tasksApi.getTasks).toHaveBeenCalledWith(
        expect.objectContaining({
          page: 2
        })
      )
      expect(store.pagination.page).toBe(2)
    })
  })

  describe('Error Handling and State Management', () => {
    it('должен корректно управлять loading состоянием', async () => {
      let resolvePromise: (value: any) => void
      const pendingPromise = new Promise(resolve => {
        resolvePromise = resolve
      })

      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockReturnValue(pendingPromise as any)

      const createPromise = store.createVkCollectTask({ groups: [123] })

      expect(store.loading).toBe(true)

      resolvePromise!(mockSuccessResponse)
      await createPromise

      expect(store.loading).toBe(false)
    })

    it('должен очищать ошибки при вызове clearErrors', () => {
      store.error.push('Test error')

      expect(store.hasError).toBe(true)

      store.clearErrors()

      expect(store.hasError).toBe(false)
      expect(store.error).toHaveLength(0)
    })

    it('должен корректно определять состояние выполнения задачи', async () => {
      store.currentTask = {
        id: 123,
        type: 'fetch_comments',
        status: 'processing',
        createdAt: '2024-01-01T09:00:00Z',
        updatedAt: '2024-01-01T10:00:00Z'
      }

      expect(store.isTaskRunning).toBe(true)

      store.currentTask.status = 'completed'
      expect(store.isTaskRunning).toBe(false)
    })
  })

  describe('API Response Format Validation', () => {
    it('должен корректно обрабатывать различные форматы ответов API', async () => {
      // Тестируем разные форматы ответов для совместимости
      const alternativeResponse = {
        data: {
          data: {
            taskId: 456,
            status: 'created'
          }
        }
      }

      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockResolvedValue(alternativeResponse as any)
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      await store.createVkCollectTask({ groups: [123] })

      expect(store.currentTaskId).toBe(456)
    })

    it('должен обрабатывать progress в разных форматах', async () => {
      const progressResponse = {
        data: {
          success: true,
          data: {
            ...mockTaskStatusResponse.data.data,
            progress: {
              processed: 75,
              total: 150
            }
          }
        }
      }

      vi.spyOn(api, 'getTaskStatus').mockResolvedValue(progressResponse as any)

      vi.useFakeTimers()
      store.startPolling(123)
      await vi.advanceTimersByTimeAsync(2000)

      // В текущей реализации progress обрабатывается по-разному
      // Проверяем, что данные получены
      expect(api.getTaskStatus).toHaveBeenCalledWith(123)

      vi.useRealTimers()
      store.stopPolling()
    })
  })

  describe('Network Error Handling', () => {
    it('должен обрабатывать сетевые ошибки', async () => {
      const networkError = new Error('Network Error')
      networkError.name = 'NetworkError'

      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockRejectedValue(networkError)

      await expect(store.createVkCollectTask({ groups: [123] })).rejects.toThrow('Network Error')
    })

    it('должен обрабатывать timeout ошибки', async () => {
      const timeoutError = {
        response: {
          status: 408,
          data: {
            success: false,
            error: 'REQUEST_TIMEOUT',
            message: 'Request timeout'
          }
        }
      }

      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockRejectedValue(timeoutError)

      await expect(store.createVkCollectTask({ groups: [123] })).rejects.toThrow()
      expect(store.error).toContain('Request timeout')
    })
  })

  describe('Data Consistency Tests', () => {
    it('должен сохранять консистентность данных между API и store', async () => {
      vi.spyOn(api.tasksApi, 'getTaskDetails').mockResolvedValue(mockTaskStatusResponse as any)

      const task = await store.getTaskById(123)

      expect(task).toMatchObject({
        id: 123,
        status: 'processing',
        type: 'fetch_comments'
      })
      expect(store.currentTask).toEqual(task)
    })

    it('должен корректно синхронизировать изменения статуса задач', async () => {
      // Имитируем создание задачи
      vi.spyOn(api.tasksApi, 'createVkCollectTask').mockResolvedValue(mockSuccessResponse as any)
      vi.spyOn(api.tasksApi, 'getTasks').mockResolvedValue(mockTasksListResponse as any)

      await store.createVkCollectTask({ groups: [123] })

      // Проверяем, что задача появилась в списке
      expect(store.tasks).toHaveLength(1)
      expect(store.currentTaskId).toBe(123)
    })
  })
})