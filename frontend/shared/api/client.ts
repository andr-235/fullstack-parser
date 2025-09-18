import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { config } from '@/shared/config'
import { AuthStorage } from '@/shared/lib/auth-storage'

// Проверяем базовый URL
if (!config.api.baseUrl) {
  console.error('API base URL is not configured. Please set NEXT_PUBLIC_API_URL environment variable.')
}

// Создаем базовый экземпляр axios
const apiClient: AxiosInstance = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - добавляем токен авторизации
apiClient.interceptors.request.use(
  config => {
    // Получаем токен через сервис
    const token = AuthStorage.getToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor - обрабатываем ошибки
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  error => {
    // Обработка 401 ошибки - редирект на логин
    if (error.response?.status === 401) {
      AuthStorage.removeToken()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }

    // Обработка сетевых ошибок
    if (!error.response) {
      console.error('Network error:', error.message)
    }

    return Promise.reject(error)
  }
)

export { apiClient }
export default apiClient
