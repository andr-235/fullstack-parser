import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import type {
  TaskCreateData,
  VkCollectTaskData,
  TaskStatus,
  CommentsParams,
  CommentsResponse,
  TasksApiType,
  GroupsApiType,
  ApiResponse,
  PaginatedResponse,
  Group
} from '@/types/api'

// Определяем URL для API в зависимости от окружения
// В Docker-окружении nginx проксирует /api/ запросы, поэтому используем относительный путь
const isDevelopment = import.meta.env.MODE === 'development'

// Проверяем, запущено ли приложение в Docker-контейнере
const isDockerEnvironment = typeof process !== 'undefined' && process.env && process.env.DOCKER_ENV === 'true'

// В development режиме используем пустую строку для Vite proxy или переменную окружения
// В production режиме (Docker) используем пустую строку для относительных путей
const apiUrl = isDevelopment ? '' : (import.meta.env.VITE_API_URL || '')

const api: AxiosInstance = axios.create({
  baseURL: apiUrl
})

// Расширяем AxiosRequestConfig для дополнительных свойств
interface ExtendedAxiosRequestConfig extends AxiosRequestConfig {
  _retry?: boolean
  retryCount?: number
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as ExtendedAxiosRequestConfig

    // Обработка ошибки 429 (Too Many Requests) с экспоненциальной задержкой
    if (error.response?.status === 429 && !originalRequest._retry) {
      originalRequest._retry = true
      const retryCount = originalRequest.retryCount || 0

      // Ограничиваем количество повторных попыток до 3
      if (retryCount < 3) {
        originalRequest.retryCount = retryCount + 1

        // Экспоненциальная задержка: 1с, 2с, 4с
        const delay = Math.pow(2, retryCount) * 1000
        await new Promise((resolve) => setTimeout(resolve, delay))
        return api(originalRequest)
      }
    }

    // Логируем ошибки 400 и 500 для отладки
    if (error.response && [400, 500].includes(error.response.status)) {
      console.error('API Error:', error.response.data || error.message)
    }

    // Обработка сетевых ошибок (ERR_NAME_NOT_RESOLVED, ECONNABORTED и т.д.)
    if (!error.response) {
      console.error('Network Error:', error.message)
      // Можно добавить уведомление для пользователя о сетевой проблеме
    }

    return Promise.reject(error)
  }
)

/**
 * Создает новую задачу сбора комментариев.
 */
export const postCreateTask = async (data: TaskCreateData): Promise<ApiResponse<{ taskId: string | number }>> => {
  return api.post('/api/tasks', data)
}

/**
 * Запускает сбор данных для задачи.
 */
export const postStartCollect = async (taskId: string | number): Promise<ApiResponse<{ taskId: string | number; status: string }>> => {
  return api.post(`/api/collect/${taskId}`)
}

/**
 * Получает статус задачи.
 */
export const getTaskStatus = async (taskId: string | number): Promise<ApiResponse<TaskStatus>> => {
  return api.get(`/api/tasks/${taskId}`, {
    headers: {
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  })
}

/**
 * Получает результаты комментариев.
 */
export const getResults = async (taskId: string | number, params: Partial<CommentsParams> = {}): Promise<ApiResponse<CommentsResponse>> => {
  const defaultParams: CommentsParams = {
    task_id: taskId,
    limit: 20,
    offset: 0,
    ...params
  }
  return api.get('/api/comments', { params: defaultParams })
}

// Tasks API
export const tasksApi: TasksApiType = {
  /**
   * Получает список задач с пагинацией.
   */
  getTasks: (params = {}) =>
    api.get('/api/tasks', { params }),

  /**
   * Создает новую VK collect задачу.
   */
  createVkCollectTask: (data: VkCollectTaskData) =>
    api.post('/api/tasks/collect', data),

  /**
   * Получает детальную информацию о задаче.
   */
  getTaskDetails: (taskId: string | number) =>
    api.get(`/api/tasks/${taskId}`, {
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    })
}

// Groups API
export const groupsApi: GroupsApiType = {
  /**
   * Загружает файл с группами VK.
   */
  uploadGroups: (formData: FormData, encoding: string = 'utf-8') =>
    api.post(`/api/groups/upload?encoding=${encodeURIComponent(encoding)}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  /**
   * Получает статус задачи загрузки групп.
   */
  getTaskStatus: (taskId: string | number) =>
    api.get(`/api/groups/upload/${taskId}/status`, {
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    }),

  /**
   * Получает список групп.
   */
  getGroups: (params = {}): Promise<PaginatedResponse<Group>> =>
    api.get('/api/groups', { params }),

  /**
   * Удаляет группу.
   */
  deleteGroup: (groupId: string | number) =>
    api.delete(`/api/groups/${groupId}`),

  /**
   * Массовое удаление групп.
   */
  deleteGroups: (groupIds: (string | number)[]) =>
    api.delete('/api/groups/batch', { data: { groupIds }}),

  /**
   * Удаляет все группы из БД.
   */
  deleteAllGroups: () =>
    api.delete('/api/groups/all'),

  /**
   * Получает все группы без пагинации (для селектов и форм).
   */
  getAllGroups: (): Promise<PaginatedResponse<Group>> =>
    api.get('/api/groups', { params: { limit: 10000, page: 1 } })
}

export default api