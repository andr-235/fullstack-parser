import { ID, LoginRequest, BaseUser } from '@/shared/types'

export type { LoginRequest }

export type UserRole = 'admin' | 'moderator' | 'user'

export interface User extends BaseUser {
  username: string
  firstName: string
  lastName: string
  avatar?: string
  role: UserRole
  createdAt: string
  updatedAt: string
}

export interface CreateUserRequest {
  email: string
  username: string
  firstName: string
  lastName: string
  password: string
  role?: UserRole
}

export interface UpdateUserRequest {
  firstName?: string
  lastName?: string
  avatar?: string
  role?: UserRole
  isActive?: boolean
}

export interface AuthResponse {
  user: User
  token: string
}
