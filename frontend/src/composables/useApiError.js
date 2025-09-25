import { ref } from 'vue'

/**
 * Composable для унифицированной обработки ошибок API
 *
 * @param {Object} options - Настройки обработки ошибок
 * @returns {Object} Объект с методами обработки ошибок
 */
export function useApiError(options = {}) {
  const {
    showToast = false,
    defaultMessage = 'Произошла ошибка при выполнении запроса'
  } = options

  const error = ref(null)
  const isError = ref(false)

  /**
   * Обрабатывает ошибку API запроса
   *
   * @param {Error} err - Ошибка
   * @param {string} customMessage - Пользовательское сообщение об ошибке
   * @returns {string} Форматированное сообщение об ошибке
   */
  const handleError = (err, customMessage = null) => {
    console.error('API Error:', err)

    let errorMessage = customMessage || defaultMessage

    if (err?.response) {
      const { status, data } = err.response

      // Обработка стандартных HTTP статусов
      switch (status) {
        case 400:
          errorMessage = data?.message || 'Неверные данные запроса'
          break
        case 401:
          errorMessage = 'Не авторизован'
          break
        case 403:
          errorMessage = 'Недостаточно прав доступа'
          break
        case 404:
          errorMessage = data?.message || 'Ресурс не найден'
          break
        case 408:
          errorMessage = 'Превышено время ожидания запроса'
          break
        case 409:
          errorMessage = data?.message || 'Конфликт данных'
          break
        case 422:
          errorMessage = data?.message || 'Ошибка валидации данных'
          break
        case 429:
          errorMessage = 'Слишком много запросов. Попробуйте позже'
          break
        case 500:
          errorMessage = 'Внутренняя ошибка сервера'
          break
        case 502:
          errorMessage = 'Сервер недоступен'
          break
        case 503:
          errorMessage = 'Сервис временно недоступен'
          break
        case 504:
          errorMessage = 'Превышено время ожидания ответа сервера'
          break
        default:
          // Попытка извлечь сообщение из ответа сервера
          if (data?.message) {
            errorMessage = data.message
          } else if (data?.error) {
            errorMessage = data.error
          } else if (data?.details) {
            errorMessage = data.details
          }
      }

      // Обработка детальных ошибок валидации
      if (data?.errors && Array.isArray(data.errors)) {
        errorMessage = data.errors.join(', ')
      }
    } else if (err?.request) {
      // Ошибка сети
      errorMessage = 'Ошибка сети. Проверьте подключение к интернету'
    } else if (err?.message) {
      // Другие ошибки
      errorMessage = err.message
    }

    error.value = {
      original: err,
      message: errorMessage,
      status: err?.response?.status,
      data: err?.response?.data,
      timestamp: new Date()
    }
    isError.value = true

    if (showToast) {
      // TODO: Интеграция с системой уведомлений (toast/snackbar)
      console.warn('Toast notification:', errorMessage)
    }

    return errorMessage
  }

  /**
   * Очищает состояние ошибки
   */
  const clearError = () => {
    error.value = null
    isError.value = false
  }

  /**
   * Проверяет, является ли ошибка определенного типа
   *
   * @param {number} status - HTTP статус код
   * @returns {boolean}
   */
  const isErrorType = (status) => {
    return error.value?.status === status
  }

  /**
   * Получает человекочитаемое описание ошибки
   *
   * @returns {string}
   */
  const getErrorDescription = () => {
    if (!error.value) return ''

    const { status, message } = error.value

    switch (status) {
      case 400:
        return 'Проверьте правильность введенных данных'
      case 401:
        return 'Необходимо войти в систему'
      case 403:
        return 'У вас нет прав для выполнения этого действия'
      case 404:
        return 'Запрашиваемый ресурс не найден'
      case 429:
        return 'Подождите несколько секунд перед повторной попыткой'
      case 500:
      case 502:
      case 503:
      case 504:
        return 'Попробуйте повторить запрос через несколько минут'
      default:
        return message || 'Обратитесь к администратору, если проблема повторяется'
    }
  }

  /**
   * Определяет, можно ли повторить запрос
   *
   * @returns {boolean}
   */
  const canRetry = () => {
    if (!error.value) return false

    const { status } = error.value

    // Можно повторить для временных ошибок сервера и сетевых ошибок
    return [408, 429, 500, 502, 503, 504].includes(status) || !status
  }

  /**
   * Оборачивает async функцию для автоматической обработки ошибок
   *
   * @param {Function} asyncFn - Асинхронная функция
   * @param {string} customMessage - Пользовательское сообщение об ошибке
   * @returns {Function} Обернутая функция
   */
  const withErrorHandling = (asyncFn, customMessage = null) => {
    return async (...args) => {
      try {
        clearError()
        return await asyncFn(...args)
      } catch (err) {
        handleError(err, customMessage)
        throw err
      }
    }
  }

  return {
    // State
    error,
    isError,

    // Methods
    handleError,
    clearError,
    isErrorType,
    getErrorDescription,
    canRetry,
    withErrorHandling
  }
}

/**
 * Глобальная утилита для обработки ошибок API
 */
export const ApiErrorHandler = {
  /**
   * Извлекает сообщение об ошибке из объекта ошибки
   *
   * @param {Error} error - Объект ошибки
   * @param {string} fallback - Резервное сообщение
   * @returns {string}
   */
  extractMessage(error, fallback = 'Произошла ошибка') {
    if (error?.response?.data?.message) {
      return error.response.data.message
    }

    if (error?.response?.data?.error) {
      return error.response.data.error
    }

    if (error?.message) {
      return error.message
    }

    return fallback
  },

  /**
   * Проверяет, является ли ошибка сетевой
   *
   * @param {Error} error - Объект ошибки
   * @returns {boolean}
   */
  isNetworkError(error) {
    return !error?.response && error?.request
  },

  /**
   * Проверяет, является ли ошибка серверной (5xx)
   *
   * @param {Error} error - Объект ошибки
   * @returns {boolean}
   */
  isServerError(error) {
    const status = error?.response?.status
    return status && status >= 500
  },

  /**
   * Проверяет, является ли ошибка клиентской (4xx)
   *
   * @param {Error} error - Объект ошибки
   * @returns {boolean}
   */
  isClientError(error) {
    const status = error?.response?.status
    return status && status >= 400 && status < 500
  },

  /**
   * Форматирует ошибки валидации
   *
   * @param {Error} error - Объект ошибки
   * @returns {Array<string>}
   */
  formatValidationErrors(error) {
    const data = error?.response?.data

    if (data?.errors && Array.isArray(data.errors)) {
      return data.errors
    }

    if (data?.details && typeof data.details === 'object') {
      return Object.values(data.details).flat()
    }

    return []
  }
}