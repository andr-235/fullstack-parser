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

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Common authentication types
export interface LoginRequest {
  email: string
  password: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface BaseUser {
  id: ID
  email: string
  is_active: boolean
}
