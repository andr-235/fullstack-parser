import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import axios from 'axios'
import { useTasksStore } from '@/stores/tasks'
import TaskStatus from '@/views/TaskStatus.vue'
import FetchComments from '@/views/FetchComments.vue'

// Мокаем axios для контроля API запросов
vi.mock('axios')
const mockedAxios = vi.mocked(axios, true)

// Мокаем Vue Router для компонентов, которые используют router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  currentRoute: {
    value: {
      params: { taskId: '1' },
      query: {}
    }
  }
}

const mockRoute = {
  params: { taskId: '1' },
  query: {}
}

describe('Frontend-Backend Integration Tests', () => {
  let wrapper
  let pinia
  let vuetify

  beforeEach(() => {
    // Очищаем все моки перед каждым тестом
    vi.clearAllMocks()

    // Создаем новые инстансы для каждого теста
    pinia = createPinia()
    vuetify = createVuetify()

    // Мокаем успешные ответы от API по умолчанию
    mockedAxios.create.mockReturnValue(mockedAxios)
    mockedAxios.interceptors = {
      response: {
        use: vi.fn()
      }
    }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  describe('Task Creation and Status Polling', () => {
    it('should create task and start polling for status updates', async () => {
      // Мокаем создание задачи
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          success: true,
          data: { taskId: 5, status: 'created' }
        }
      })

      // Мокаем получение статуса задачи (последовательно)
      mockedAxios.get
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: {
              id: 5,
              status: 'pending',
              type: 'fetch_comments',
              progress: { processed: 0, total: 0 },
              errors: [],
              groups: [123, 456]
            }
          }
        })
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: {
              id: 5,
              status: 'processing',
              type: 'fetch_comments',
              progress: { processed: 50, total: 100 },
              errors: [],
              groups: [123, 456]
            }
          }
        })
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: {
              id: 5,
              status: 'completed',
              type: 'fetch_comments',
              progress: { processed: 100, total: 100 },
              errors: [],
              groups: [123, 456]
            }
          }
        })

      const store = useTasksStore(pinia)

      // Создаем задачу
      const result = await store.createVkCollectTask({
        groups: [123, 456]
      })

      expect(result.taskId).toBe(5)
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/tasks/collect', {
        groups: [123, 456]
      })

      // Запускаем polling
      store.startPolling(5)

      // Ждем несколько циклов polling
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/tasks/5', {
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      })

      store.stopPolling()
    })

    it('should handle API errors during task creation', async () => {
      // Мокаем ошибку API
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 400,
          data: {
            success: false,
            error: 'Validation failed: groups is required'
          }
        }
      })

      const store = useTasksStore(pinia)

      await expect(store.createVkCollectTask({ groups: [] })).rejects.toThrow()
      expect(store.hasError).toBe(true)
      expect(store.errorMessage).toContain('Validation failed')
    })

    it('should handle network errors gracefully', async () => {
      // Мокаем сетевую ошибку
      mockedAxios.post.mockRejectedValueOnce(new Error('Network Error'))

      const store = useTasksStore(pinia)

      await expect(store.createVkCollectTask({ groups: [123] })).rejects.toThrow()
      expect(store.hasError).toBe(true)
    })
  })

  describe('TaskStatus Component Integration', () => {
    it('should display task details and handle status updates', async () => {
      // Мокаем API response для получения деталей задачи
      mockedAxios.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            id: 1,
            status: 'processing',
            type: 'fetch_comments',
            priority: 0,
            progress: { processed: 75, total: 100 },
            errors: [],
            groups: [123, 456],
            parameters: { token: '***' },
            startedAt: '2023-01-01T10:00:00Z',
            createdAt: '2023-01-01T09:00:00Z'
          }
        }
      })

      wrapper = mount(TaskStatus, {
        global: {
          plugins: [pinia, vuetify],
          mocks: {
            $router: mockRouter,
            $route: mockRoute
          }
        }
      })

      await wrapper.vm.$nextTick()

      // Проверяем, что компонент отображает корректную информацию
      expect(wrapper.text()).toContain('processing')
      expect(wrapper.text()).toContain('75')
      expect(wrapper.text()).toContain('100')

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/tasks/1', expect.any(Object))
    })

    it('should handle task not found error', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 404,
          data: {
            success: false,
            error: 'Task not found'
          }
        }
      })

      wrapper = mount(TaskStatus, {
        global: {
          plugins: [pinia, vuetify],
          mocks: {
            $router: mockRouter,
            $route: mockRoute
          }
        }
      })

      await wrapper.vm.$nextTick()

      // Ждем обработки ошибки
      await new Promise(resolve => setTimeout(resolve, 100))

      expect(wrapper.text()).toContain('Ошибка') // Предполагаем, что компонент показывает ошибку
    })
  })

  describe('API Response Format Validation', () => {
    it('should handle different API response formats correctly', async () => {
      const store = useTasksStore(pinia)

      // Тестируем различные форматы ответов, которые может вернуть API

      // Формат 1: { success: true, data: { taskId, status } }
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          success: true,
          data: { taskId: 1, status: 'created' }
        }
      })

      let result = await store.createVkCollectTask({ groups: [123] })
      expect(result.taskId).toBe(1)

      // Формат 2: Прямой ответ без обертки
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          id: 1,
          status: 'processing',
          progress: { processed: 50, total: 100 }
        }
      })

      result = await store.getTaskById(1)
      expect(result.status).toBe('processing')
    })

    it('should handle inconsistent API response structures', async () => {
      const store = useTasksStore(pinia)

      // Тестируем случай, когда API возвращает данные в разных обертках
      mockedAxios.get
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: {
              id: 1,
              status: 'pending'
            }
          }
        })
        .mockResolvedValueOnce({
          data: {
            id: 1,
            status: 'processing'
          }
        })

      // Первый запрос с оберткой success/data
      let result = await store.getTaskById(1)
      expect(result.status).toBe('pending')

      // Второй запрос без обертки
      result = await store.getTaskById(1)
      expect(result.status).toBe('processing')
    })
  })

  describe('Pending Tasks Behavior', () => {
    it('should handle tasks stuck in pending status', async () => {
      const store = useTasksStore(pinia)

      // Мокаем задачу, которая остается в pending статусе
      mockedAxios.get.mockResolvedValue({
        data: {
          success: true,
          data: {
            id: 5,
            status: 'pending',
            type: 'fetch_comments',
            progress: { processed: 0, total: 0 },
            errors: [],
            groups: [123],
            startedAt: null,
            finishedAt: null
          }
        }
      })

      store.startPolling(5)

      // Ждем несколько циклов polling
      await new Promise(resolve => setTimeout(resolve, 6000))

      // Проверяем, что polling продолжается для pending задач
      expect(mockedAxios.get).toHaveBeenCalledTimes(3) // 3 запроса за 6 секунд с интервалом 2 сек

      store.stopPolling()
    })

    it('should stop polling when task completes', async () => {
      const store = useTasksStore(pinia)

      // Мокаем последовательность: pending -> processing -> completed
      mockedAxios.get
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: { id: 5, status: 'pending' }
          }
        })
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: { id: 5, status: 'processing' }
          }
        })
        .mockResolvedValueOnce({
          data: {
            success: true,
            data: { id: 5, status: 'completed' }
          }
        })

      store.startPolling(5)

      // Ждем завершения
      await new Promise(resolve => setTimeout(resolve, 7000))

      // Polling должен остановиться после completed статуса
      expect(store.polling).toBeNull()
    })
  })

  describe('HTTP Request Headers and CORS', () => {
    it('should include proper headers for cache control', async () => {
      const store = useTasksStore(pinia)

      mockedAxios.get.mockResolvedValue({
        data: { success: true, data: { id: 1, status: 'processing' } }
      })

      await store.getTaskById(1)

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/tasks/1', {
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      })
    })

    it('should handle CORS preflight requests properly', async () => {
      // Этот тест сложно полноценно проверить в unit тестах,
      // но мы можем убедиться, что axios сконфигурирован правильно

      expect(mockedAxios.create).toHaveBeenCalled()
      expect(mockedAxios.interceptors.response.use).toHaveBeenCalled()
    })
  })

  describe('Error Recovery and Retry Logic', () => {
    it('should retry requests on 429 (rate limit) errors', async () => {
      const store = useTasksStore(pinia)

      // Первый запрос - 429 ошибка
      // Второй запрос - успех
      mockedAxios.get
        .mockRejectedValueOnce({
          response: { status: 429 },
          config: {}
        })
        .mockResolvedValueOnce({
          data: { success: true, data: { id: 1, status: 'processing' } }
        })

      const result = await store.getTaskById(1)
      expect(result.status).toBe('processing')
    })

    it('should stop polling on repeated errors', async () => {
      const store = useTasksStore(pinia)

      // Мокаем постоянные ошибки
      mockedAxios.get.mockRejectedValue(new Error('Server error'))

      store.startPolling(5)

      // Ждем несколько попыток
      await new Promise(resolve => setTimeout(resolve, 3000))

      // Polling должен остановиться при ошибках
      expect(store.polling).toBeNull()
      expect(store.hasError).toBe(true)
    })
  })

  describe('Data Synchronization', () => {
    it('should keep task list and current task in sync', async () => {
      const store = useTasksStore(pinia)

      // Мокаем список задач
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: [
            { id: 1, status: 'pending' },
            { id: 2, status: 'completed' }
          ],
          total: 2
        }
      })

      await store.fetchTasks()
      expect(store.tasks).toHaveLength(2)

      // Мокаем обновление конкретной задачи
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: { id: 1, status: 'processing' }
        }
      })

      await store.getTaskById(1)
      expect(store.currentTask.status).toBe('processing')

      // После обновления статуса, список должен обновиться
      mockedAxios.get.mockResolvedValueOnce({
        data: {
          success: true,
          data: [
            { id: 1, status: 'processing' },
            { id: 2, status: 'completed' }
          ],
          total: 2
        }
      })

      await store.fetchTasks()
      const updatedTask = store.tasks.find(t => t.id === 1)
      expect(updatedTask.status).toBe('processing')
    })
  })
})