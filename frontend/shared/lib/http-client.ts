/**
 * Базовый HTTP клиент с retry логикой и обработкой ошибок
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

export class HttpClient {
  private baseURL: string
  private getAuthToken: (() => string | null) | undefined

  constructor(baseURL: string = API_BASE_URL, getAuthToken?: () => string | null) {
    this.baseURL = baseURL
    this.getAuthToken = getAuthToken
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    }

    // Добавляем токен авторизации если он есть
    const token = this.getAuthToken?.()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const config: RequestInit = {
      headers,
      ...options,
    }

    const maxRetries = 3
    let lastError: Error | null = null

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        const response = await fetch(url, config)

        if (!response.ok) {
          // Для ошибок 503 и 429 делаем retry
          if ((response.status === 503 || response.status === 429) && attempt < maxRetries - 1) {
            const delay = Math.pow(2, attempt) * 1000
            await new Promise(resolve => setTimeout(resolve, delay))
            continue
          }

          const errorMessage = await this.parseError(response)
          throw new Error(errorMessage)
        }

        return await response.json()
      } catch (err) {
        lastError = err instanceof Error ? err : new Error('Unknown error')

        if (attempt === maxRetries - 1) {
          throw lastError
        }
      }
    }

    throw lastError || new Error('Request failed')
  }

  private async parseError(response: Response): Promise<string> {
    let errorMessage = `HTTP error! status: ${response.status}`

    try {
      if (response.status === 500) {
        const errorText = await response.text()
        if (errorText?.trim()) {
          return errorText.trim()
        }
      }

      const errorData = await response.json()

      if (errorData.error?.message) {
        return errorData.error.message
      }

      if (errorData.message) {
        return errorData.message
      }

      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          const validationErrors = errorData.detail
            .map((err: any) => {
              const field = err.loc ? err.loc.slice(1).join('.') : 'field'
              return `${field}: ${err.msg}`
            })
            .join('; ')
          return `Validation error: ${validationErrors}`
        }

        if (typeof errorData.detail === 'string') {
          return errorData.detail
        }

        return `Server error: ${JSON.stringify(errorData.detail)}`
      }

      if (errorData.error?.detail) {
        return errorData.error.detail
      }

      if (typeof errorData === 'string') {
        return errorData
      }

      if (errorData && typeof errorData === 'object') {
        const stringFields = Object.values(errorData).filter(
          (value): value is string => typeof value === 'string'
        )
        if (stringFields.length > 0) {
          return stringFields[0]!
        }
        return `Server error: ${JSON.stringify(errorData)}`
      }
    } catch {
      // Fallback to status text
      return response.statusText || errorMessage
    }

    return errorMessage
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const queryString = params
      ? new URLSearchParams(
          Object.entries(params).filter(([_, value]) => value !== undefined)
        ).toString()
      : ''

    const fullEndpoint = `${endpoint}${queryString ? `?${queryString}` : ''}`
    return this.request(fullEndpoint)
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : null,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : null,
    })
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : null,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request(endpoint, {
      method: 'DELETE',
    })
  }
}

// Создаем HTTP клиент с поддержкой авторизации
export const httpClient = new HttpClient(API_BASE_URL, () => {
  // Получаем токен из localStorage (будет обновлен через AuthProvider)
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth-storage') 
      ? JSON.parse(localStorage.getItem('auth-storage') || '{}').state?.accessToken || null
      : null
  }
  return null
})
