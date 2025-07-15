/**
 * Базовые типы API на основе FastAPI схем backend
 */

// Базовые типы
export interface BaseEntity {
  id: number
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  total: number
  skip: number
  limit: number
  items: T[]
}

export interface StatusResponse {
  success: boolean
  message: string
}

export interface APIError {
  detail: string
  status_code: number
}

export interface PaginationParams {
  skip?: number
  limit?: number
}
