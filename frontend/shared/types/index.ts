// Shared types
export type ID = string | number

export interface ApiResponse<T = any> {
  data: T
  success: boolean
  message?: string
}

export interface PaginationParams {
  page: number
  limit: number
}

export interface PaginatedResponse<T = any> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
  }
}
