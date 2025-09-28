import { ref } from 'vue'

interface ErrorConfig {
  showToast?: boolean
  defaultMessage?: string
}

interface ApiErrorInfo {
  original: any
  message: any
  status: any
  data: any
  timestamp: Date
}

export function useApiError(config: ErrorConfig = {}) {
  const lastError = ref<ApiErrorInfo | null>(null)
  const isNetworkError = ref(false)

  const defaultConfig = {
    showToast: config.showToast ?? true,
    defaultMessage: config.defaultMessage ?? 'Произошла ошибка при запросе к серверу'
  }

  const handleError = (err: any): string => {
    const errorInfo: ApiErrorInfo = {
      original: err,
      message: extractErrorMessage(err),
      status: extractErrorStatus(err),
      data: extractErrorData(err),
      timestamp: new Date()
    }

    lastError.value = errorInfo
    isNetworkError.value = isNetworkErrorType(err)

    if (defaultConfig.showToast) {
      // В реальном приложении здесь будет показ toast уведомления
      console.error('API Error:', errorInfo.message)
    }

    return errorInfo.message
  }

  const extractErrorMessage = (err: any): string => {
    if (!err) return defaultConfig.defaultMessage

    // Axios error response
    if (err.response?.data) {
      const data = err.response.data

      if (typeof data === 'string') return data
      if (data.message) return data.message
      if (data.error) return data.error
      if (data.errors) {
        if (Array.isArray(data.errors)) {
          return data.errors.join(', ')
        }
        if (typeof data.errors === 'object') {
          return Object.values(data.errors).flat().join(', ')
        }
      }
    }

    // Axios error message
    if (err.message) return err.message

    // Error object
    if (err instanceof Error) return err.message

    // Fallback
    return defaultConfig.defaultMessage
  }

  const extractErrorStatus = (err: any): number | null => {
    if (err.response?.status) return err.response.status
    if (err.status) return err.status
    return null
  }

  const extractErrorData = (err: any): any => {
    if (err.response?.data) return err.response.data
    if (err.data) return err.data
    return null
  }

  const isNetworkErrorType = (err: any): boolean => {
    if (!err) return false

    // No response means network error
    if (!err.response) return true

    // Common network error codes
    const networkStatuses = [0, 408, 502, 503, 504, 522, 524]
    return networkStatuses.includes(err.response?.status)
  }

  const getStatusText = (status: any): string => {
    const statusTexts: Record<number, string> = {
      400: 'Неверный запрос',
      401: 'Не авторизован',
      403: 'Доступ запрещен',
      404: 'Не найдено',
      422: 'Ошибка валидации',
      429: 'Слишком много запросов',
      500: 'Внутренняя ошибка сервера',
      502: 'Плохой шлюз',
      503: 'Сервис недоступен',
      504: 'Таймаут шлюза'
    }

    return statusTexts[status] || `Ошибка ${status}`
  }

  const withErrorHandling = async (asyncFn: any, ...args: any[]) => {
    try {
      return await asyncFn(...args)
    } catch (error) {
      handleError(error)
      throw error
    }
  }

  const retry = async (
    fn: () => Promise<any>,
    maxAttempts: number = 3,
    delay: number = 1000
  ): Promise<any> => {
    let lastError: any

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn()
      } catch (error: any) {
        lastError = error
        handleError(error)

        if (attempt === maxAttempts) break

        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, delay * attempt))
      }
    }

    throw lastError
  }

  const isValidationError = (error: any): boolean => {
    return extractErrorStatus(error) === 422
  }

  const isAuthError = (error: any): boolean => {
    const status = extractErrorStatus(error)
    return status === 401 || status === 403
  }

  const isServerError = (error: any): boolean => {
    const status = extractErrorStatus(error)
    return status ? status >= 500 : false
  }

  const getValidationErrors = (error: any): Record<string, string[]> => {
    const data = extractErrorData(error)
    if (data?.errors && typeof data.errors === 'object') {
      return data.errors
    }
    return {}
  }

  return {
    lastError,
    isNetworkError,
    handleError,
    withErrorHandling,
    retry,
    isValidationError,
    isAuthError,
    isServerError,
    getValidationErrors,
    getStatusText
  }
}