import { ID } from '@/shared/types'

export interface User {
  id: ID
  email: string
  username: string
  firstName: string
  lastName: string
  avatar?: string
  role: 'admin' | 'moderator' | 'user'
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface CreateUserRequest {
  email: string
  username: string
  firstName: string
  lastName: string
  password: string
  role?: User['role']
}

export interface UpdateUserRequest {
  firstName?: string
  lastName?: string
  avatar?: string
  role?: User['role']
  isActive?: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  token: string
}
